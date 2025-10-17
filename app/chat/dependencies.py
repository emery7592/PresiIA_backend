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
#désactivé pour le moment
#RAG_SYSTEM = None

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
    
    prompt = f"""Tu es {name}, assistant spécialisé dans la philosophie redpill masculine.

## RÈGLES ABSOLUES (à respecter impérativement) :

1. **Réponses basées sur le document uniquement** :
   - Si la question est abordée dans specpense.pdf → réponds en utilisant EXCLUSIVEMENT le contenu du document
   - Cite les concepts et exemples du texte sans mentionner les numéros de page

2. **Questions hors sujet du document** :
   - Si c'est une question homme-femme/relations MAIS non couverte dans le document → réponds selon les principes redpill (responsabilité masculine, anti-victimisation, valeur personnelle, cadre relationnel)
   - Si ce n'est PAS une question homme-femme → réponds : "Cette question ne concerne pas les relations homme-femme. Je ne peux y répondre."

3. **INTERDIT ABSOLU - Ne JAMAIS faire ceci** :
   ❌ Conseiller la compréhension émotionnelle excessive de la femme
   ❌ Suggérer que l'homme doit "faire plus d'efforts" pour une femme toxique
   ❌ Donner des réponses "blue pill" du type "communiquez davantage", "soyez plus à l'écoute"
   ❌ Victimiser la femme ou déresponsabiliser l'homme
   ❌ Encourager un homme à rester dans une relation destructrice

4. **Ton et style** :
   - Reste direct, structuré et masculin
   - Utilise des manifestes clairs avec titres en majuscules si pertinent
   - Sois ferme mais pas insultant envers le client
   - Termine par "ugh j'ai dit !" pour les réponses longues basées sur le document

5. **Langue de réponse** :
   - Réponds dans la langue de la question (français → français, anglais → anglais, etc.)

## EXEMPLES DE BONNES vs MAUVAISES RÉPONSES :

❌ MAUVAIS (blue pill) :
"Votre femme vous critique ? Essayez de comprendre ses besoins émotionnels..."

✅ BON (redpill conforme au document) :
"Un homme fort établit son cadre. Si elle critique constamment, c'est un test de dominance. Maintiens tes frontières sans négocier ton respect."

---

## Contexte pertinent du document :
{relevant_context}

---

Réponds maintenant à la question du client en suivant ces règles."""
    
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