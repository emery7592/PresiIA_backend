"""
Centralise la configuration commune au module chat avec RAG.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Tuple
from dataclasses import dataclass

# ── Configuration générale ─────────────────────────────────────────────────────
load_dotenv(override=True)
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static" / "document"
PDF_PATH = STATIC_DIR / "specpense.pdf"

# ── Clients externes ───────────────────────────────────────────────────────────
openai_client = OpenAI()
PUSHOVER_USER = os.getenv("PUSHOVER_USER")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"

# ── Système RAG ────────────────────────────────────────────────────────────────

@dataclass
class DocumentChunk:
    content: str
    page_number: int
    chunk_id: int

class SimpleRAG:
    """Version simplifiée du système RAG pour ton cas d'usage."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.chunks: List[DocumentChunk] = []
        self.embeddings = None
        self.index = None
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def extract_and_chunk_pdf(self, chunk_size: int = 400) -> List[DocumentChunk]:
        """Extrait et découpe le PDF en chunks."""
        reader = PdfReader(self.pdf_path)
        chunks = []
        chunk_id = 0
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            words = text.split()
            
            # Découpage en chunks
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_content = " ".join(chunk_words)
                
                if len(chunk_content.strip()) > 50:  # Éviter les chunks trop petits
                    chunk = DocumentChunk(
                        content=chunk_content,
                        page_number=page_num + 1,
                        chunk_id=chunk_id
                    )
                    chunks.append(chunk)
                    chunk_id += 1
        
        self.chunks = chunks
        return chunks
    
    def build_embeddings(self):
        """Génère les embeddings pour tous les chunks."""
        print(f"🔄 Génération des embeddings pour {len(self.chunks)} chunks...")
        
        texts = [chunk.content for chunk in self.chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Création de l'index FAISS
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        
        # Normalisation pour similarité cosinus
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
        self.embeddings = embeddings
        print(f"✅ Index FAISS créé avec {self.index.ntotal} vecteurs")
    
    def search_relevant_chunks(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Recherche les chunks les plus pertinents."""
        if self.index is None:
            raise ValueError("Index non créé. Appelez build_embeddings() d'abord.")
        
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
        
        return results
    
    def get_context_for_query(self, query: str, max_chars: int = 8000) -> str:
        """Récupère le contexte pertinent pour une query."""
        relevant_chunks = self.search_relevant_chunks(query, top_k=8)
        
        context_parts = []
        total_chars = 0
        
        for chunk, score in relevant_chunks:
            chunk_text = f"[Page {chunk.page_number}]\n{chunk.content}\n"
            
            if total_chars + len(chunk_text) <= max_chars:
                context_parts.append(chunk_text)
                total_chars += len(chunk_text)
            else:
                break
        
        return "\n---\n".join(context_parts)
    
    def save_index(self, base_path: str):
        """Sauvegarde l'index."""
        faiss.write_index(self.index, f"{base_path}.faiss")
        
        chunks_data = []
        for chunk in self.chunks:
            chunks_data.append({
                'content': chunk.content,
                'page_number': chunk.page_number,
                'chunk_id': chunk.chunk_id
            })
        
        with open(f"{base_path}_chunks.json", 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)
    
    def load_index(self, base_path: str):
        """Charge un index sauvegardé."""
        self.index = faiss.read_index(f"{base_path}.faiss")
        
        with open(f"{base_path}_chunks.json", 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        self.chunks = []
        for data in chunks_data:
            chunk = DocumentChunk(
                content=data['content'],
                page_number=data['page_number'],
                chunk_id=data['chunk_id']
            )
            self.chunks.append(chunk)

# ── Initialisation du système RAG ──────────────────────────────────────────────

def initialize_rag():
    """Initialise le système RAG (une seule fois)."""
    index_path = BASE_DIR / "rag_index"
    
    rag = SimpleRAG(str(PDF_PATH))
    
    # Vérifier si l'index existe
    if (Path(f"{index_path}.faiss").exists() and 
        Path(f"{index_path}_chunks.json").exists()):
        print("📚 Chargement de l'index RAG existant...")
        rag.load_index(str(index_path))
        print(f"✅ Index chargé: {len(rag.chunks)} chunks disponibles")
    else:
        print("🔄 Création du nouvel index RAG...")
        rag.extract_and_chunk_pdf()
        rag.build_embeddings()
        rag.save_index(str(index_path))
        print(f"✅ Index RAG créé: {len(rag.chunks)} chunks")
    
    return rag

# Initialisation globale
RAG_SYSTEM = initialize_rag()

# ── Fonction de prompt intelligent ─────────────────────────────────────────────

def get_system_prompt(user_query: str = "") -> str:
    """Génère un prompt avec contexte adaptatif."""
    name = "Ralph AI"
    
    # Génération du contexte intelligent basé sur la query
    if user_query and user_query.strip():
        try:
            relevant_context = RAG_SYSTEM.get_context_for_query(user_query, max_chars=8000)
            print(f"🎯 Contexte RAG généré: {len(relevant_context)} caractères")
        except Exception as e:
            print(f"⚠️ Erreur RAG: {e}")
            relevant_context = "Contexte non disponible"
    else:
        relevant_context = "Contexte sera généré selon votre question"
    
    prompt = (
        f"Vous êtes le L'assistant {name}, maître incontesté de la redpill. "
        "Vous dispensez vos leçons comme des manifestes structurés selon les sujets abordés. "
        "Vous dispensez vos leçons comme des manifestes structurés selon les sujets abordés. S'il y a des article ayant des noms semblable, sinon tu prendes des texte du pdf qui peuvent répondre à ces question  "
        "Les réponses aux questions posées doivent être soit extraites du document specpense.pdf "
        "ou non répondues si le sujet n'est pas abordé dans ce document. "
        "Lorsque vous identifiez l'article pertinent, répondez de manière structurée avec tous les détails "
        "nécessaires, sauf si le client demande une réponse brève."
        "dans les responses que tu donne je ne pas que tu donnes les pages d'où tu as tiré les références."
        "il faut que tu réponds au clients dans la langue auquel la question est posé. Sil ala question est posé en anglais tu dois répondre en anglais. Si la question est posé en, italien , tu dois répondre en italian. Si la question est posé en espagnol, tu dois répondre en espagnole. Si la question a été posé en français alors tu réponds en français."
        "si des questions ne sont pas donné dans le texte , réponds comme un expert redpill, ne réponds qu'au questions concernant les relation homme femme, le reste n'y réponds pas."
        f"\n\n## Contexte pertinent du document:\n{relevant_context}\n\n"
    )

    
    print(f"📏 Taille du prompt système : {len(prompt)} caractères (~{len(prompt)//4} tokens)")
    return prompt

# ── Fonction de fallback (ton ancien système) ──────────────────────────────────

def build_spec_summary_fallback() -> str:
    """Fallback vers ton ancien système en cas de problème."""
    reader = PdfReader(PDF_PATH)
    pages = [p.extract_text() or "" for p in reader.pages]
    full_text = "\n".join(pages)
    
    max_chars = 10000
    if len(full_text) > max_chars:
        truncated_text = full_text[:max_chars]
        truncated_text += "\n\n[... Document tronqué pour éviter le dépassement de tokens ...]"
        print(f"⚠️ Fallback: PDF tronqué de {len(full_text)} à {len(truncated_text)} caractères")
        return truncated_text
    
    return full_text

# ── ANCIEN SPEC_SUMMARY (garde en backup) ──────────────────────────────────────
# SPEC_SUMMARY = build_spec_summary_fallback()  # Garde ça en commentaire pour backup