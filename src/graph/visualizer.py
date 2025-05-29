"""
Graph Visualizer Module

Handles visualization of NetworkX graphs using pyvis and matplotlib.
"""

import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class VisualizationConfig:
    """Configuration for graph visualization."""
    layout_type: str = "Force-directed (default)"
    node_size_multiplier: float = 1.0
    enable_physics: bool = True
    spring_strength: float = 0.04
    central_gravity: float = 0.3
    show_labels: bool = True
    edge_width: int = 2
    color_scheme: str = "Default"
    height: str = "600px"
    width: str = "100%"


class GraphVisualizer:
    """Handles graph visualization using pyvis and matplotlib."""
    
    def __init__(self, config: VisualizationConfig = None):
        self.config = config or VisualizationConfig()
        self.color_schemes = {
            "Default": {
                "main": "#FF6B6B", "word_sense": "#FFB347"
            },
            "Pastel": {
                "main": "#FFB3BA", "word_sense": "#FFC985"
            },
            "Vibrant": {
                "main": "#FF0000", "word_sense": "#FF8C00"
            },
            "Monochrome": {
                "main": "#2C2C2C", "word_sense": "#777777"
            }
        }
        
        # POS-based colors for synsets
        self.pos_colors = {
            "Default": {
                "n": "#FFB6C1",  # Light pink for nouns
                "v": "#87CEEB",  # Sky blue for verbs
                "a": "#98FB98",  # Pale green for adjectives
                "s": "#98FB98",  # Pale green for adjective satellites (same as adjectives)
                "r": "#DDA0DD"   # Plum purple for adverbs
            },
            "Pastel": {
                "n": "#FFD1DC",  # Pastel pink for nouns
                "v": "#B0E0E6",  # Powder blue for verbs
                "a": "#F0FFF0",  # Honeydew for adjectives
                "s": "#F0FFF0",  # Honeydew for adjective satellites
                "r": "#E6E6FA"   # Lavender for adverbs
            },
            "Vibrant": {
                "n": "#FF1493",  # Deep pink for nouns
                "v": "#0000FF",  # Blue for verbs
                "a": "#00FF00",  # Lime green for adjectives
                "s": "#00FF00",  # Lime green for adjective satellites
                "r": "#8A2BE2"   # Blue violet for adverbs
            },
            "Monochrome": {
                "n": "#696969",  # Dim gray for nouns
                "v": "#808080",  # Gray for verbs
                "a": "#A9A9A9",  # Dark gray for adjectives
                "s": "#A9A9A9",  # Dark gray for adjective satellites
                "r": "#C0C0C0"   # Silver for adverbs
            }
        }
    
    def visualize_interactive(self, G: nx.Graph, node_labels: Dict, 
                            word: str, save_path: str = None) -> Optional[str]:
        """Create an interactive visualization using pyvis."""
        if G.number_of_nodes() == 0:
            print("No graph to display - no WordNet connections found.")
            return None
        
        # Create pyvis network
        net = Network(
            height=self.config.height,
            width=self.config.width,
            bgcolor="#ffffff",
            font_color="black",
            directed=True
        )
        
        # Configure physics
        self._configure_physics(net)
        
        # Add nodes and edges
        self._add_nodes(net, G, node_labels)
        self._add_edges(net, G)
        
        # Generate HTML and inject JavaScript
        if save_path:
            # Save to file with JavaScript injection
            import tempfile
            import os
            
            # Create temporary file first
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
            temp_file.close()  # Close the file handle before using it
            net.save_graph(temp_file.name)
            
            # Read the HTML and inject our JavaScript
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Get navigation JavaScript
            navigation_js = self._add_navigation_js(net)
            
            # Inject our navigation JavaScript before closing body tag
            html_content = html_content.replace('</body>', navigation_js + '</body>')
            
            # Write to the final save path
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except PermissionError:
                # On Windows, sometimes the file is still locked
                pass
            
            return save_path
        else:
            # For Streamlit display, generate HTML with JavaScript
            import tempfile
            import os
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
            temp_file.close()  # Close the file handle before using it
            net.save_graph(temp_file.name)
            
            # Read the HTML and inject our JavaScript
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Get navigation JavaScript
            navigation_js = self._add_navigation_js(net)
            
            # Inject our navigation JavaScript before closing body tag
            html_content = html_content.replace('</body>', navigation_js + '</body>')
            
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except PermissionError:
                # On Windows, sometimes the file is still locked
                pass
            
            return html_content
    
    def visualize_static(self, G: nx.Graph, node_labels: Dict, 
                        word: str, save_path: str = None) -> Optional[str]:
        """Create a static visualization using matplotlib."""
        if G.number_of_nodes() == 0:
            print("No graph to display - no WordNet connections found.")
            return None
        
        plt.figure(figsize=(12, 8))
        
        # Use spring layout for positioning
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Draw nodes by type
        colors = self.color_schemes.get(self.config.color_scheme, 
                                       self.color_schemes["Default"])
        pos_colors = self.pos_colors.get(self.config.color_scheme, self.pos_colors["Default"])
        
        main_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'main']
        
        if main_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=main_nodes, 
                                 node_color=colors["main"], 
                                 node_size=800, alpha=0.8)
        
        # Draw synset nodes by POS
        synset_nodes_by_pos = {}
        for n, d in G.nodes(data=True):
            if d.get('node_type') == 'synset':
                pos = d.get('pos', 'n')
                if pos not in synset_nodes_by_pos:
                    synset_nodes_by_pos[pos] = []
                synset_nodes_by_pos[pos].append(n)
        
        for pos, nodes in synset_nodes_by_pos.items():
            color = pos_colors.get(pos, pos_colors.get('n', '#FFB6C1'))
            nx.draw_networkx_nodes(G, pos, nodelist=nodes, 
                                 node_color=color, 
                                 node_size=600, alpha=0.8, node_shape='s')
        
        # Draw edges with colors
        self._draw_colored_edges(G, pos)
        
        # Add labels if enabled
        if self.config.show_labels:
            nx.draw_networkx_labels(G, pos, node_labels, font_size=10)
        
        plt.title(f"WordNet Graph for '{word}'", size=16)
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.show()
            return None
    
    def _configure_physics(self, net: Network):
        """Configure physics settings for the network."""
        if self.config.enable_physics:
            physics_options = f"""
            var options = {{
              "physics": {{
                "enabled": true,
                "stabilization": {{"iterations": 100}},
                "barnesHut": {{
                  "gravitationalConstant": -8000,
                  "centralGravity": {self.config.central_gravity},
                  "springLength": 95,
                  "springConstant": {self.config.spring_strength},
                  "damping": 0.09
                }}
              }}
            }}
            """
        else:
            physics_options = """
            var options = {
              "physics": {"enabled": false}
            }
            """
        net.set_options(physics_options)
    
    def _add_nodes(self, net: Network, G: nx.Graph, node_labels: Dict):
        """Add nodes to the pyvis network."""
        colors = self.color_schemes.get(self.config.color_scheme, 
                                       self.color_schemes["Default"])
        
        for node in G.nodes():
            node_data = G.nodes[node]
            node_type = node_data.get('node_type', 'unknown')
            
            # Configure node based on type
            if node_type == 'breadcrumb':
                color = '#CCCCCC'
                size = int(20 * self.config.node_size_multiplier)
                title = f"Back to: {node_data.get('original_word', 'Previous word')}"
                node_style = {
                    'borderWidth': 3,
                    'borderWidthSelected': 4,
                    'borderDashes': [5, 5],
                    'chosen': True
                }
            elif node_type == 'main':
                color = colors["main"]
                size = int(30 * self.config.node_size_multiplier)
                title = f"Main word: {node_data.get('word', '').upper()}"
                node_style = {}
            elif node_type == 'word_sense':
                color = colors.get("word_sense", "#FFB347")  # Orange for word senses
                size = int(25 * self.config.node_size_multiplier)
                synset_name = node_data.get('synset_name', node)
                definition = node_data.get('definition', 'No definition')
                word = node_data.get('word', '')
                sense_num = node_data.get('sense_number', '')
                title = f"Word sense: {word} (sense {sense_num})\nSynset: {synset_name}\nDefinition: {definition}"
                node_style = {'shape': 'diamond'}
            elif node_type == 'synset':
                # Get POS for color selection
                pos = node_data.get('pos', 'n')  # Default to noun if POS not found
                pos_colors = self.pos_colors.get(self.config.color_scheme, self.pos_colors["Default"])
                color = pos_colors.get(pos, pos_colors.get('n', '#FFB6C1'))  # Default to noun color
                size = int(25 * self.config.node_size_multiplier)
                synset_name = node_data.get('synset_name', node)
                definition = node_data.get('definition', 'No definition')
                pos_label = node_data.get('pos_label', 'noun')
                title = f"Synset: {node_labels.get(node, node)}\nPOS: {pos_label}\nSynset: {synset_name}\nDefinition: {definition}"
                node_style = {'shape': 'square'}
            else:
                color = colors.get("synset", "#CCCCCC")
                size = int(20 * self.config.node_size_multiplier)
                title = f"Node: {node_labels.get(node, node)}"
                node_style = {}
            
            # Create node configuration
            label = node_labels.get(node, node) if self.config.show_labels else ""
            node_config = {
                'label': label,
                'color': color,
                'size': size,
                'title': title,
                'font': {'size': int(12 * self.config.node_size_multiplier), 'color': 'black'}
            }
            node_config.update(node_style)
            
            net.add_node(node, **node_config)
    
    def _add_edges(self, net: Network, G: nx.Graph):
        """Add edges to the pyvis network."""
        edge_colors = {
            'sense': '#666666',
            'hypernym': '#FF4444',
            'hyponym': '#FF4444',  # Same color as hypernym
            'meronym': '#44AA44',  # Same color as holonym
            'holonym': '#44AA44'
        }
        
        for source, target, edge_data in G.edges(data=True):
            relation = edge_data.get('relation', 'unknown')
            color = edge_data.get('color', edge_colors.get(relation, '#888888'))
            arrow_direction = edge_data.get('arrow_direction', 'to')
            
            # Initialize actual_source and actual_target for all cases
            actual_source, actual_target = source, target
            
            # For taxonomic relationships, ensure consistent direction: specific → general
            if relation in ['hypernym', 'hyponym']:
                # Always make taxonomic arrows go specific → general (consistent direction)
                if relation == 'hypernym':
                    # Hypernym means source is more specific than target
                    # So arrow should go source → target (specific → general)
                    actual_source, actual_target = source, target
                elif relation == 'hyponym':
                    # Hyponym means source is more general than target
                    # So arrow should go target → source (specific → general)
                    actual_source, actual_target = target, source
            else:
                # For non-taxonomic relationships, handle reverse arrow direction normally
                if arrow_direction == 'from':
                    actual_source, actual_target = target, source
                else:
                    actual_source, actual_target = source, target
            
            # Create accurate tooltip based on the VISUAL arrow direction
            source_name = actual_source.split('.')[0] if '.' in actual_source else actual_source.split('_')[-1]
            target_name = actual_target.split('.')[0] if '.' in actual_target else actual_target.split('_')[-1]
            
            # Generate semantic description based on the visual arrow direction
            if relation == 'sense':
                description = f"Word sense connection: {source_name} → {target_name}"
            elif relation in ['hypernym', 'hyponym']:
                # Both hypernyms and hyponyms now have consistent visual direction: specific → general
                description = f"Is-a relationship: {source_name} is a type of {target_name}"
            elif relation in ['member_meronym', 'substance_meronym', 'part_meronym']:
                description = f"Part-of relationship: {source_name} is part of {target_name}"
            elif relation in ['member_holonym', 'substance_holonym', 'part_holonym']:
                description = f"Has-part relationship: {source_name} has part {target_name}"
            elif relation == 'similar_to':
                description = f"Similar to: {source_name} is similar to {target_name}"
            elif relation == 'antonym':
                description = f"Opposite of: {source_name} is opposite to {target_name}"
            elif relation == 'also':
                description = f"Related to: {source_name} is also related to {target_name}"
            elif relation in ['entailment', 'entails']:
                description = f"Entails: {source_name} entails {target_name}"
            elif relation in ['cause', 'causes']:
                description = f"Causes: {source_name} causes {target_name}"
            else:
                description = f"{relation.replace('_', ' ').title()}: {source_name} → {target_name}"
            
            edge_config = {
                'color': color,
                'width': self.config.edge_width + 1 if relation != 'sense' else self.config.edge_width,
                'title': description,
                'arrows': 'to'
            }
            
            net.add_edge(actual_source, actual_target, **edge_config)
    
    def _add_navigation_js(self, net: Network):
        """Add JavaScript for double-click navigation with enhanced console logging."""
        navigation_js = """
        <script type="text/javascript">
        window.addEventListener('load', function() {
            setTimeout(function() {
                if (window.network) {
                    // Enhanced console logging for double-click events
                    window.network.on("doubleClick", function (params) {
                        if (params.nodes.length > 0) {
                            const nodeId = params.nodes[0];
                            
                            // Get node data from the network
                            const nodeData = window.network.body.data.nodes.get(nodeId);
                            
                            // Enhanced console logging with detailed information
                            console.group('🖱️ Node Double-Click Event');
                            console.log('Node ID:', nodeId);
                            console.log('Node Label:', nodeData ? nodeData.label : 'Unknown');
                            console.log('Node Title:', nodeData ? nodeData.title : 'Unknown');
                            console.log('Node Color:', nodeData ? nodeData.color : 'Unknown');
                            console.log('Node Size:', nodeData ? nodeData.size : 'Unknown');
                            console.log('Click Position:', params.pointer.DOM);
                            console.log('Canvas Position:', params.pointer.canvas);
                            console.log('Timestamp:', new Date().toISOString());
                            
                            // Log node type detection
                            let nodeType = 'unknown';
                            let targetWord = nodeId;
                            
                            if (nodeId.includes('_main')) {
                                nodeType = 'main word';
                                targetWord = nodeId.replace('_main', '');
                            } else if (nodeId.includes('_breadcrumb')) {
                                nodeType = 'breadcrumb';
                                targetWord = nodeId.replace('_breadcrumb', '');
                            } else if (nodeId.includes('_word')) {
                                nodeType = 'related word';
                                targetWord = nodeId.replace('_word', '');
                            } else if (nodeId.includes('.')) {
                                nodeType = 'synset';
                                targetWord = nodeId.split('.')[0];
                            }
                            
                            console.log('Detected Node Type:', nodeType);
                            console.log('Target Word for Navigation:', targetWord);
                            console.groupEnd();
                            
                            // Navigate by setting URL parameter
                            const url = new URL(window.location);
                            url.searchParams.set('navigate_to', targetWord);
                            url.searchParams.set('clicked_node', nodeId);
                            window.location.href = url.toString();
                        } else {
                            console.log('🖱️ Double-click detected but no nodes selected');
                        }
                    });
                    
                    // Also log single clicks for additional debugging
                    window.network.on("click", function (params) {
                        if (params.nodes.length > 0) {
                            const nodeId = params.nodes[0];
                            const nodeData = window.network.body.data.nodes.get(nodeId);
                            console.log('🖱️ Single-click on node:', nodeId, '| Label:', nodeData ? nodeData.label : 'Unknown');
                        }
                    });
                    
                    // Log when hovering over nodes
                    window.network.on("hoverNode", function (params) {
                        const nodeId = params.node;
                        const nodeData = window.network.body.data.nodes.get(nodeId);
                        console.log('🖱️ Hovering over node:', nodeId, '| Label:', nodeData ? nodeData.label : 'Unknown');
                    });
                    
                    console.log('✅ Enhanced double-click navigation and logging enabled');
                    console.log('💡 Double-click any node to see detailed logging information');
                } else {
                    console.log('⚠️ Network not found, retrying...');
                    // Retry after a longer delay
                    setTimeout(arguments.callee, 1000);
                }
            }, 500);
        });
        </script>
        """
        return navigation_js
    
    def _draw_colored_edges(self, G: nx.Graph, pos: Dict):
        """Draw edges with different colors based on relationship type."""
        edge_colors = {
            'sense': '#666666',
            'hypernym': '#FF4444',
            'hyponym': '#FF4444',  # Same color as hypernym
            'meronym': '#44AA44',  # Same color as holonym
            'holonym': '#44AA44'
        }
        
        # Group edges by relationship type
        edges_by_type = {}
        for source, target, data in G.edges(data=True):
            relation = data.get('relation', 'unknown')
            arrow_direction = data.get('arrow_direction', 'to')
            
            # Handle reverse arrow direction by swapping source and target
            if arrow_direction == 'from':
                actual_edge = (target, source)
            else:
                actual_edge = (source, target)
                
            if relation not in edges_by_type:
                edges_by_type[relation] = []
            edges_by_type[relation].append(actual_edge)
        
        # Draw each group with its color
        for relation, edges in edges_by_type.items():
            color = edge_colors.get(relation, '#888888')
            nx.draw_networkx_edges(G, pos, edgelist=edges, 
                                 edge_color=color, width=2, alpha=0.7) 