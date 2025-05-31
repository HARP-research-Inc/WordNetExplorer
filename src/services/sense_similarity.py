"""
Sense similarity calculation service using embeddings.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import streamlit as st
from dataclasses import dataclass


@dataclass
class SenseScore:
    """Container for sense similarity scores."""
    synset_name: str
    definition: str
    definition_score: Optional[float] = None
    context_score: Optional[float] = None
    combined_score: Optional[float] = None
    
    @property
    def max_score(self) -> float:
        """Get the maximum score across all scoring methods."""
        scores = [s for s in [self.definition_score, self.context_score, self.combined_score] if s is not None]
        return max(scores) if scores else 0.0


class SenseSimilarityCalculator:
    """Calculate similarity between user input and WordNet senses."""
    
    def __init__(self):
        """Initialize the similarity calculator."""
        self.embedder = self._load_embedder()
    
    @staticmethod  
    @st.cache_resource
    def _load_embedder():
        """Load the sentence embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            # Use a lightweight model for efficiency
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model
        except ImportError:
            st.warning("sentence-transformers not installed. Using fallback similarity. "
                      "Install it with: pip install sentence-transformers")
            return None
        except Exception as e:
            st.warning(f"Error loading sentence transformer: {e}")
            return None
    
    def compute_embeddings(self, texts: List[str]) -> np.ndarray:
        """Compute embeddings for a list of texts."""
        if self.embedder is None:
            # Fallback: simple TF-IDF-like representation
            return self._fallback_embeddings(texts)
        
        return self.embedder.encode(texts, convert_to_numpy=True)
    
    def _fallback_embeddings(self, texts: List[str]) -> np.ndarray:
        """Simple fallback embedding using word overlap."""
        # This is a very basic fallback - in production, you'd want sentence-transformers
        from sklearn.feature_extraction.text import TfidfVectorizer
        try:
            vectorizer = TfidfVectorizer(max_features=100)
            return vectorizer.fit_transform(texts).toarray()
        except:
            # Ultimate fallback: random embeddings (not useful, but prevents crashes)
            return np.random.rand(len(texts), 100)
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def _detect_pos_from_context(self, word: str, context: str) -> Optional[str]:
        """Detect the part of speech of a word in context using simple heuristics."""
        try:
            import nltk
            from nltk import pos_tag, word_tokenize
            
            # Try to download required data
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            
            try:
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                nltk.download('averaged_perceptron_tagger', quiet=True)
            
            # Tokenize and tag the context
            tokens = word_tokenize(context.lower())
            pos_tags = pos_tag(tokens)
            
            # Find the word in the context and get its POS tag
            word_lower = word.lower()
            for token, pos_tag_result in pos_tags:
                if token == word_lower or token.replace('_', ' ') == word_lower:
                    # Map NLTK POS tags to WordNet POS
                    if pos_tag_result.startswith('NN'):  # Noun
                        return 'n'
                    elif pos_tag_result.startswith('VB'):  # Verb
                        return 'v'
                    elif pos_tag_result.startswith('JJ'):  # Adjective
                        return 'a'
                    elif pos_tag_result.startswith('RB'):  # Adverb
                        return 'r'
            
            return None
            
        except Exception:
            # Fallback: return None if POS tagging fails
            return None
    
    def _filter_synsets_by_pos(self, synsets: List, limit_pos_to_context: bool, selected_pos: List[str], context_input: Optional[str], word: str) -> List:
        """Filter synsets based on part of speech settings."""
        if not synsets:
            return synsets
        
        # Create mapping from UI options to WordNet POS codes
        pos_mapping = {
            'Nouns': 'n',
            'Verbs': 'v', 
            'Adjectives': ['a', 's'],  # Both regular and satellite adjectives
            'Adverbs': 'r'
        }
        
        # Get allowed POS codes from selected_pos
        allowed_pos_codes = set()
        if selected_pos:
            for pos_name in selected_pos:
                pos_codes = pos_mapping.get(pos_name, [])
                if isinstance(pos_codes, str):
                    pos_codes = [pos_codes]
                allowed_pos_codes.update(pos_codes)
        else:
            # If no specific POS selected, allow all
            allowed_pos_codes = {'n', 'v', 'a', 's', 'r'}
        
        # If limit_pos_to_context is enabled, detect POS from context
        context_pos = None
        if limit_pos_to_context and context_input:
            context_pos = self._detect_pos_from_context(word, context_input)
            if context_pos:
                # Only keep synsets that match the detected POS
                allowed_pos_codes = {context_pos}
        
        # Filter synsets
        filtered_synsets = []
        for synset in synsets:
            synset_pos = synset.pos()
            if synset_pos in allowed_pos_codes:
                filtered_synsets.append(synset)
        
        return filtered_synsets
    
    def calculate_sense_similarities(
        self, 
        word: str,
        synsets: List,
        definition_input: Optional[str] = None,
        context_input: Optional[str] = None,
        limit_pos_to_context: bool = False,
        selected_pos: List[str] = None
    ) -> List[SenseScore]:
        """Calculate similarity scores for all senses of a word."""
        if not synsets:
            return []
        
        # Filter synsets based on part of speech settings
        filtered_synsets = self._filter_synsets_by_pos(synsets, limit_pos_to_context, selected_pos, context_input, word)
        
        if not filtered_synsets:
            return []
        
        # Extract synset information
        synset_info = []
        for synset in filtered_synsets:
            synset_info.append({
                'name': synset.name(),
                'definition': synset.definition(),
                'examples': synset.examples(),
                'pos': synset.pos()
            })
        
        scores = []
        
        # Compute definition similarities if requested
        definition_scores = {}
        if definition_input:
            definitions = [info['definition'] for info in synset_info]
            all_texts = [definition_input] + definitions
            embeddings = self.compute_embeddings(all_texts)
            
            input_embedding = embeddings[0]
            for i, info in enumerate(synset_info):
                def_embedding = embeddings[i + 1]
                similarity = self.cosine_similarity(input_embedding, def_embedding)
                definition_scores[info['name']] = similarity
        
        # Compute context similarities if requested
        context_scores = {}
        if context_input:
            # For context, we'll compare against definitions + examples
            context_texts = []
            synset_names = []
            
            for info in synset_info:
                # Combine definition with examples for better context matching
                combined_text = info['definition']
                if info['examples']:
                    combined_text += " " + " ".join(info['examples'])
                context_texts.append(combined_text)
                synset_names.append(info['name'])
            
            all_texts = [context_input] + context_texts
            embeddings = self.compute_embeddings(all_texts)
            
            input_embedding = embeddings[0]
            for i, name in enumerate(synset_names):
                context_embedding = embeddings[i + 1]
                similarity = self.cosine_similarity(input_embedding, context_embedding)
                context_scores[name] = similarity
        
        # Create SenseScore objects
        for info in synset_info:
            name = info['name']
            def_score = definition_scores.get(name)
            ctx_score = context_scores.get(name)
            
            # Calculate combined score if both are available
            combined = None
            if def_score is not None and ctx_score is not None:
                combined = (def_score + ctx_score) / 2
            
            scores.append(SenseScore(
                synset_name=name,
                definition=info['definition'],
                definition_score=def_score,
                context_score=ctx_score,
                combined_score=combined
            ))
        
        # Sort by maximum score
        scores.sort(key=lambda x: x.max_score, reverse=True)
        
        return scores


def get_sense_similarity_calculator():
    """Get or create a cached instance of the similarity calculator."""
    return SenseSimilarityCalculator() 