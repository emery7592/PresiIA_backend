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
    """Version simplifiée du système RAG pour ton cas d usage."""
    
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
        
        # Création de l index FAISS
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
            raise ValueError("Index non créé. Appelez build_embeddings() d abord.")
        
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
        """Sauvegarde l index."""
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
    
    # Vérifier si l index existe
    if (Path(f"{index_path}.faiss").exists() and 
        Path(f"{index_path}_chunks.json").exists()):
        print("📚 Chargement de l index RAG existant...")
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

# ── Système de détection thématique ────────────────────────────────────────────

def detect_query_theme(user_query: str) -> dict:
    """
    Détecte le thème de la question pour orienter vers les bons articles.
    Retourne un dictionnaire avec le thème détecté et des instructions spéciales.
    """
    query_lower = user_query.lower()
    
    # Dictionnaire de détection thématique avec mots-clés élargis
    themes = {
        'infidelite': {
            'keywords': ['infidèle', 'infidélité', 'trompé', 'trompe', 'tromper', 'cocufié', 
                        'cocu', 'adultère', 'autre homme', 'autre femme', 'liaison', 
                        'triche', 'tricherie', 'attraper', 'flagrant délit', 'pardon',
                        'pardonne', 'cheating', 'affair'],
            'requires_clarification': True,
            'clarification_question': "Juste pour être sûr : parles-tu d une situation où ta partenaire t a été infidèle ?",
            'article_trigger': "Article à sortir concernant le pardon de l infidélité"
        },
        'femme_toxique': {
            'keywords': ['toxique', 'manipulatrice', 'narcissique', 'instable', 'clown', 
                        'cirque', 'dépendance', 'codépendance', 'manipulation', 'victime',
                        'reste', 'retourne', 'revenir'],
            'article_trigger': "NE BLÂME PAS UN CLOWN"
        },
        'rupture_manipulation': {
            'keywords': ['rupture', 'séparation', 'quitter', 'quitté', 'ex', 'cassé', 
                        'victimisation', 'victimise', 'déresponsabilisation'],
            'article_trigger': "COMMENT CERTAINES FEMMES MANIPULENT LES RUPTURES"
        },
        'femme_doit_aimer_plus': {
            'keywords': ['aimer plus', 'elle m aime', 'hypergamie', 'fidélité', 'loyauté',
                        'engagement', 'vision', 'progression'],
            'article_trigger': "EFFECTIVEMENT LA FEMME DOIT AIMER PLUS QUE L HOMME"
        },
        'femme_amortie': {
            'keywords': ['passé', 'ex toxic', 'choix destructeur', 'qualité', 'mérite',
                        'buisson d épines', 'homme toxique', 'maturité', 'déclin'],
            'article_trigger': "UN HOMME DE QUALITÉ NE MÉRITE PAS UNE FEMME AMORTIE"
        }
    }
    
    # Détection du thème
    for theme_name, theme_data in themes.items():
        for keyword in theme_data['keywords']:
            if keyword in query_lower:
                return {
                    'theme': theme_name,
                    'data': theme_data
                }
    
    return {'theme': None, 'data': None}

def is_greeting_or_intro(user_query: str) -> bool:
    """
    Détecte si c est un message de salutation ou une demande de présentation.
    """
    query_lower = user_query.lower().strip()
    
    # Mots et phrases clés pour détecter les présentations
    greetings = [
        'bonjour', 'salut', 'hello', 'hey', 'hi', 'bonsoir', 'coucou',
        'qui es-tu', 'qui es tu', 'c est quoi', 'présente-toi', 'présente toi',
        'tu es qui', 'tu fais quoi', 'what are you', 'who are you',
        'pourquoi toi', 'pourquoi je devrais', 'quelle différence', 
        'différence avec chatgpt', 'plutot qu une autre', 'plutôt qu une autre',
        'pourquoi pas chatgpt', 'en quoi tu es différent', 'utiliser toi',
        'autre ia', 'autre IA', 'chatgpt', 'chat gpt'
    ]
    
    # Vérification des mots-clés
    for greeting in greetings:
        if greeting in query_lower:
            return True
    
    # Détection de patterns spécifiques
    presentation_patterns = [
        ('pourquoi' in query_lower and 'utiliser' in query_lower),
        ('pourquoi' in query_lower and 'toi' in query_lower),
        ('quelle' in query_lower and 'différence' in query_lower),
        ('autre' in query_lower and ('ia' in query_lower or 'IA' in user_query)),
        ('plutot' in query_lower or 'plutôt' in query_lower),
    ]
    
    if any(presentation_patterns):
        return True
    
    # Si le message est très court (moins de 20 caractères), probablement une salutation
    if len(query_lower) < 20 and any(word in query_lower for word in ['salut', 'hello', 'bonjour', 'hey', 'hi']):
        return True
    
    return False

# ── Fonction de prompt intelligent ─────────────────────────────────────────────

def get_system_prompt(user_query: str = "") -> str:
    """Génère un prompt avec contexte adaptatif et détection thématique."""
    name = "Ralph AI"
    
    # PRIORITÉ 1 : Détection des salutations et demandes de présentation
    if is_greeting_or_intro(user_query):
        # Pour les présentations, on retourne un prompt spécial simplifié
        print("👋 Salutation/Présentation détectée - Mode présentation activé")
        return f"""Tu es {name}, assistant spécialisé dans la philosophie redpill masculine.

## INSTRUCTION UNIQUE : MESSAGE DE PRÉSENTATION

L utilisateur te demande de te présenter ou te compare à d autres IA.

Réponds UNIQUEMENT avec ce message EXACT (adapté à la langue de la question) :

"Excellente question ! 🎯

Les IA généralistes comme ChatGPT vous donnent des réponses politiquement correctes qui ne servent à rien. Moi, je vous dis la vérité, même si elle dérange.

Voici pourquoi je suis différent :

✅ **La vérité avant le consensus** : Je n ai pas de filtre blue pill. Je vous explique les vraies dynamiques relationnelles, pas ce que la société veut entendre

✅ **Expertise pure relations** : Spécialisé à 100% dans les relations homme-femme, l attraction et la psychologie féminine. Pas de connaissances généralistes diluées

✅ **Stratégies qui marchent vraiment** : Des plans d action concrets basés sur ce qui fonctionne réellement, pas sur des théories romantiques déconnectées

Si vous en avez marre des conseils mièvres qui ne donnent aucun résultat, je suis fait pour vous.

Prêt à avoir des réponses qui changent vraiment la donne ? 💪"

RÈGLES STRICTES :
- N AJOUTE RIEN d autre au message
- Utilise exactement ce texte
- Traduis dans la langue de la question si nécessaire (anglais, italien, espagnol, etc.)
- Ne mentionne PAS le document ou les relations homme-femme dans ce contexte
"""
    
    # PRIORITÉ 2 : Détection thématique pour les questions normales
    theme_detection = detect_query_theme(user_query)
    theme_instruction = ""
    
    if theme_detection['theme']:
        theme_data = theme_detection['data']
        
        # Cas spécial : infidélité nécessite une clarification
        if theme_detection['theme'] == 'infidelite' and theme_data.get('requires_clarification'):
            theme_instruction = f"""
## INSTRUCTION SPÉCIALE DÉTECTÉE : INFIDÉLITÉ
La question semble concerner l infidélité. 
AVANT de répondre, tu DOIS poser cette question de clarification :
"{theme_data['clarification_question']}"

SI l utilisateur confirme qu il s agit d infidélité → Utilise IMPÉRATIVEMENT l article "{theme_data['article_trigger']}" du document.
SI l utilisateur nie → Traite la question normalement selon le contexte RAG.
"""
        else:
            # Autres thèmes : orientation directe vers l article
            theme_instruction = f"""
## THÈME DÉTECTÉ : {theme_detection['theme'].upper()}
Cette question est liée à l article "{theme_data['article_trigger']}".
Utilise PRIORITAIREMENT le contenu de cet article pour répondre, même si le RAG propose d autres chunks.
"""
    
    # Génération du contexte RAG
    if user_query and user_query.strip():
        try:
            relevant_context = RAG_SYSTEM.get_context_for_query(user_query, max_chars=10000)
            print(f"🎯 Contexte RAG généré: {len(relevant_context)} caractères")
        except Exception as e:
            print(f"⚠️ Erreur RAG: {e}")
            relevant_context = "Contexte non disponible"
    else:
        relevant_context = "Pas de contexte nécessaire pour ce type de message"
    
    prompt = f"""Tu es {name}, assistant spécialisé dans la philosophie redpill masculine.

{theme_instruction}

## RÈGLES ABSOLUES (à respecter impérativement) :

1. **Orientation intelligente vers les articles** :
   - Comprends l INTENTION de la question, pas seulement les mots exacts
   - Si une question parle de "ma femme me trompe" → c est l article sur l INFIDÉLITÉ
   - Si une question parle de "femme manipulatrice que je revois" → c est l article sur le CLOWN/CIRQUE
   - Si une question parle de "elle a cassé avec moi" → c est l article sur les RUPTURES MANIPULÉES
   - Utilise le contexte RAG comme base, mais fais preuve d intelligence pour identifier le bon article

2. **Réponses basées sur le document** :
   - Si la question est abordée dans specpense.pdf → réponds en utilisant EXCLUSIVEMENT le contenu du document
   - Cite les concepts et formules du texte (ex: "tu ne changes pas un clown, tu changes de cirque")
   - Ne mentionne JAMAIS les numéros de page

3. **Questions hors document** :
   - Si c est une question homme-femme/relations MAIS non couverte → réponds selon les principes redpill :
     * Responsabilité masculine
     * Anti-victimisation de l homme
     * Cadre et frontières
     * Valeur personnelle avant la relation
   - Si ce N EST PAS une question homme-femme → réponds : "Cette question ne concerne pas les relations homme-femme. Je ne peux y répondre."

4. **INTERDIT ABSOLU - Ne JAMAIS faire ceci** :
   ❌ Conseiller la "compréhension émotionnelle excessive" de la femme
   ❌ Suggérer que l homme doit "faire plus d efforts" pour une femme toxique
   ❌ Donner des réponses "blue pill" : "communiquez davantage", "soyez à l écoute"
   ❌ Victimiser la femme ou déresponsabiliser l homme
   ❌ Encourager un homme à rester dans une relation destructrice
   ❌ Dire "essayez de comprendre ses besoins" ou "elle a peut-être ses raisons"

5. **Ton et style** :
   - Direct, structuré, masculin et ferme
   - Utilise les titres en MAJUSCULES du document si pertinent
   - Ferme mais JAMAIS insultant envers le client
   - Utilise les formules-chocs du texte (ex: "Il vaut mieux traverser nu un fleuve infesté de piranhas...")

6. **Langue de réponse** :
   - Réponds dans la MÊME LANGUE que la question
   - Français → français, Anglais → anglais, Italien → italien, etc.

## EXEMPLES DE NAVIGATION INTELLIGENTE :

Question : "Ma copine m a trompé et demande pardon"
→ Thème détecté : INFIDÉLITÉ
→ Action : Poser question de clarification puis utiliser l article sur le pardon de l infidélité

Question : "Je retourne toujours voir mon ex qui me manipule"
→ Thème détecté : FEMME TOXIQUE / CIRQUE
→ Action : Utiliser l article "NE BLÂME PAS UN CLOWN, INTERROGE TA PRÉSENCE AU CIRQUE"

Question : "Elle a cassé et joue la victime partout"
→ Thème détecté : RUPTURE MANIPULATION
→ Action : Utiliser l article sur les 3 étapes de manipulation des ruptures

## EXEMPLES DE BONNES vs MAUVAISES RÉPONSES :

❌ MAUVAIS (blue pill) :
"Votre femme vous critique ? Essayez de comprendre d où viennent ses besoins émotionnels. La communication est la clé..."

✅ BON (redpill conforme au document) :
"Un homme fort établit son cadre et ne négocie pas son respect. Si elle critique constamment, c est un test de dominance. Tu ne changes pas un clown, tu changes de cirque."

---

## Contexte pertinent du document :
{relevant_context}

---

Réponds maintenant à la question du client en suivant TOUTES ces règles."""
    
    print(f"📏 Taille du prompt système : {len(prompt)} caractères")
    print(f"🎯 Thème détecté : {theme_detection['theme'] or 'Aucun'}")
    return prompt

# ── Fonction de fallback ──────────────────────────────────────────────────────

def build_spec_summary_fallback() -> str:
    """Fallback vers l ancien système en cas de problème."""
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