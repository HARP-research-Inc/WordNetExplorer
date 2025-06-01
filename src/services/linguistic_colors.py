"""
Linguistic color mappings for visualization.
"""


class LinguisticColors:
    """Color mappings for linguistic visualizations."""
    
    @staticmethod
    def get_pos_color(pos_tag: str) -> str:
        """Get color for a POS tag."""
        # Map detailed POS tags to colors
        if pos_tag.startswith('NN'):  # Nouns
            return '#FFB6C1'
        elif pos_tag.startswith('VB'):  # Verbs
            return '#98D8C8'
        elif pos_tag.startswith('JJ'):  # Adjectives
            return '#F7DC6F'
        elif pos_tag.startswith('RB'):  # Adverbs
            return '#BB8FCE'
        elif pos_tag in ['DT', 'PRP', 'PRP$', 'WDT', 'WP', 'WP$']:  # Determiners/Pronouns
            return '#85C1E2'
        elif pos_tag in ['IN', 'TO']:  # Prepositions
            return '#F8C471'
        elif pos_tag in ['CC']:  # Conjunctions
            return '#ABEBC6'
        else:
            return '#D5D8DC'  # Default gray
    
    @staticmethod
    def get_dependency_color(dep: str) -> str:
        """Get color for a dependency relation."""
        # Core grammatical relations
        if dep in ['nsubj', 'nsubjpass']:
            return '#FF6B6B'  # Red - subjects
        elif dep in ['dobj', 'iobj', 'pobj']:
            return '#4ECDC4'  # Teal - objects
        elif dep in ['amod', 'advmod', 'nummod']:
            return '#95E1D3'  # Mint - modifiers
        elif dep == 'ROOT':
            return '#FFD93D'  # Gold - root
        elif dep in ['aux', 'auxpass', 'cop']:
            return '#6BCB77'  # Green - auxiliaries
        elif dep in ['prep', 'pcomp']:
            return '#FF8B94'  # Pink - prepositions
        else:
            return '#B4B4B4'  # Gray - other
    
    # Edge colors for syntactic tree visualization
    EDGE_COLORS = {
        'sconj': '#FF6B6B',      # Red - subordinating conjunction
        'iclause': '#4ECDC4',    # Teal - independent clause
        'dclause': '#95E1D3',    # Mint - dependent clause
        'tverb': '#FFD93D',      # Gold - main verb
        'subj': '#FF8B94',       # Pink - subject
        'obj': '#6BCB77',        # Green - object
        'adv': '#BB8FCE',        # Purple - adverb
        'adj': '#F7DC6F',        # Yellow - adjective
        'prep': '#F8C471',       # Orange - preposition
        'det': '#85C1E2',        # Light blue - determiner
        'aux': '#ABEBC6',        # Light green - auxiliary
        'head': '#4169E1',       # Royal blue - head of phrase
        'prep_phrase': '#FF7F50', # Coral - prepositional phrase
        'pobj': '#00CED1',       # Dark turquoise - object of preposition
        'num': '#FF69B4',        # Hot pink - numeral
        'poss': '#9370DB',       # Medium purple - possessive
        'compound': '#20B2AA',   # Light sea green - compound
        'adv_mod': '#E6E6FA',    # Lavender - adverb modifier
        'main_clause': '#87CEFA', # Light sky blue - main clause
        'verb_head': '#FFB347',   # Light orange - verb head
        'particle': '#DDA0DD',    # Plum - particle
        'obj_group': '#98FB98',   # Pale green - object group
        'part': '#F0E68C'        # Khaki - part of group
    }
    
    # Node colors for syntactic tree
    NODE_COLORS = {
        'sentence': '#FFD700',   # Gold
        'clause': '#87CEEB',     # Sky blue
        'phrase': '#DDA0DD',     # Plum
        'word': None            # Determined by POS
    } 