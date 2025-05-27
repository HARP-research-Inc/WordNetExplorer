"""
Graph Visualizer Module

Handles visualization of NetworkX graphs using pyvis and matplotlib.
"""

import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
from typing import Dict, Optional
from dataclasses import dataclass
import time


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
                "main": "#FF6B6B", "synset": "#DDA0DD"
            },
            "Pastel": {
                "main": "#FFB3BA", "synset": "#BFBFFF"
            },
            "Vibrant": {
                "main": "#FF0000", "synset": "#9932CC"
            },
            "Monochrome": {
                "main": "#2C2C2C", "synset": "#5A5A5A"
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
        
        main_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'main']
        synset_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'synset']
        
        if main_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=main_nodes, 
                                 node_color=colors["main"], 
                                 node_size=800, alpha=0.8)
        
        if synset_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=synset_nodes, 
                                 node_color=colors["synset"], 
                                 node_size=600, alpha=0.8)
        
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
            elif node_type == 'synset':
                color = colors["synset"]
                size = int(25 * self.config.node_size_multiplier)
                synset_name = node_data.get('synset_name', node)
                definition = node_data.get('definition', 'No definition')
                title = f"Word sense: {node_labels.get(node, node)}\\nSynset: {synset_name}\\nDefinition: {definition}"
                node_style = {}
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
            'hyponym': '#4488FF',
            'meronym': '#44AA44',
            'holonym': '#FFAA00'
        }
        
        relation_descriptions = {
            'sense': 'Word sense connection',
            'hypernym': 'Is a type of (more general)',
            'hyponym': 'Type includes (more specific)',
            'meronym': 'Has part',
            'holonym': 'Part of'
        }
        
        for source, target, edge_data in G.edges(data=True):
            relation = edge_data.get('relation', 'unknown')
            color = edge_data.get('color', edge_colors.get(relation, '#888888'))
            description = relation_descriptions.get(relation, relation)
            
            edge_config = {
                'color': color,
                'width': self.config.edge_width + 1 if relation != 'sense' else self.config.edge_width,
                'title': description,
                'arrows': 'to'
            }
            
            net.add_edge(source, target, **edge_config)
    
    def _add_navigation_js(self, net: Network):
        """Add JavaScript for double-click navigation with enhanced console logging."""
        timestamp = int(time.time())  # Cache-busting timestamp
        
        navigation_js = f"""
        <script type="text/javascript">
        // Cache-busting timestamp: {timestamp}
        console.log('🔧 Loading navigation JavaScript v{timestamp}');
        
        window.addEventListener('load', function() {{
            setTimeout(function() {{
                if (window.network) {{
                    console.log('✅ Network found, setting up enhanced double-click navigation v{timestamp}');
                    
                    // Enhanced console logging for double-click events
                    window.network.on("doubleClick", function (params) {{
                        if (params.nodes.length > 0) {{
                            const nodeId = params.nodes[0];
                            
                            // Get node data from the network
                            const nodeData = window.network.body.data.nodes.get(nodeId);
                            
                            // Enhanced console logging with detailed information
                            console.group('🖱️ Node Double-Click Event v{timestamp}');
                            console.log('Node ID:', nodeId);
                            console.log('Node Label:', nodeData ? nodeData.label : 'Unknown');
                            console.log('Node Title:', nodeData ? nodeData.title : 'Unknown');
                            console.log('Node Color:', nodeData ? nodeData.color : 'Unknown');
                            console.log('Node Size:', nodeData ? nodeData.size : 'Unknown');
                            console.log('Click Position:', params.pointer.DOM);
                            console.log('Canvas Position:', params.pointer.canvas);
                            console.log('Timestamp:', new Date().toISOString());
                            
                            // Enhanced node type detection with detailed logging
                            let nodeType = 'unknown';
                            let targetWord = nodeId;
                            
                            console.log('🔍 Node ID Analysis v{timestamp}:');
                            console.log('  - nodeId:', nodeId);
                            console.log('  - nodeId.startsWith("ROOT_"):', nodeId.startsWith('ROOT_'));
                            console.log('  - nodeId.includes("_main"):', nodeId.includes('_main'));
                            console.log('  - nodeId.includes("_breadcrumb"):', nodeId.includes('_breadcrumb'));
                            console.log('  - nodeId.includes("_word"):', nodeId.includes('_word'));
                            console.log('  - nodeId.includes("."):', nodeId.includes('.'));
                            
                            if (nodeId.startsWith('ROOT_')) {{
                                nodeType = 'main word (ROOT)';
                                targetWord = nodeId.replace('ROOT_', '').toLowerCase();
                                console.log('✅ Detected ROOT_ prefix v{timestamp}');
                            }} else if (nodeId.includes('_main')) {{
                                nodeType = 'main word';
                                targetWord = nodeId.replace('_main', '');
                                console.log('✅ Detected _main suffix v{timestamp}');
                            }} else if (nodeId.includes('_breadcrumb')) {{
                                nodeType = 'breadcrumb';
                                targetWord = nodeId.replace('_breadcrumb', '');
                                console.log('✅ Detected _breadcrumb suffix v{timestamp}');
                            }} else if (nodeId.includes('_word')) {{
                                nodeType = 'related word';
                                targetWord = nodeId.replace('_word', '');
                                console.log('✅ Detected _word suffix v{timestamp}');
                            }} else if (nodeId.includes('.')) {{
                                nodeType = 'synset';
                                targetWord = nodeId.split('.')[0];
                                console.log('✅ Detected synset format v{timestamp}');
                            }} else {{
                                console.log('❌ No pattern matched - using nodeId as targetWord v{timestamp}');
                            }}
                            
                            console.log('🎯 Final Detection Results v{timestamp}:');
                            console.log('  - Detected Node Type:', nodeType);
                            console.log('  - Target Word for Navigation:', targetWord);
                            console.groupEnd();
                            
                            // Create navigation data with correct message type
                            const navigationData = {{
                                type: 'streamlit-navigate',  // Fixed: match the listener type
                                targetWord: targetWord,
                                clickedNode: nodeId,
                                timestamp: new Date().toISOString(),
                                jsVersion: '{timestamp}'
                            }};
                            
                            console.log('📤 Preparing navigation v{timestamp}:', navigationData);
                            
                            // Primary approach: postMessage to parent
                            let messageSent = false;
                            
                            console.log('🔍 Parent Window Analysis v{timestamp}:');
                            console.log('  - window.parent exists:', !!window.parent);
                            console.log('  - window.parent !== window:', window.parent !== window);
                            console.log('  - window.top exists:', !!window.top);
                            console.log('  - window.top !== window:', window.top !== window);
                            
                            // Try sending to parent first (most common case for Streamlit iframes)
                            if (window.parent && window.parent !== window) {{
                                try {{
                                    // For Streamlit, we can use '*' since it's same-origin in most cases
                                    // In production, you might want to specify the exact origin
                                    window.parent.postMessage(navigationData, '*');
                                    console.log('✅ Graph: Message sent to window.parent v{timestamp}');
                                    messageSent = true;
                                }} catch (e) {{
                                    console.log('❌ Graph: Failed to send to window.parent v{timestamp}:', e);
                                }}
                            }}
                            
                            // Try sending to top window as backup
                            if (!messageSent && window.top && window.top !== window) {{
                                try {{
                                    window.top.postMessage(navigationData, '*');
                                    console.log('✅ Graph: Message sent to window.top v{timestamp}');
                                    messageSent = true;
                                }} catch (e) {{
                                    console.log('❌ Graph: Failed to send to window.top v{timestamp}:', e);
                                }}
                            }}
                            
                            // Fallback for standalone HTML files (direct navigation)
                            if (!messageSent) {{
                                console.log('🔄 Graph: Using fallback direct navigation v{timestamp}');
                                try {{
                                    const url = new URL(window.location);
                                    url.searchParams.set('word', targetWord);
                                    url.searchParams.set('clicked_node', nodeId);
                                    console.log('🔗 Graph: Direct navigation (standalone) v{timestamp}:', url.toString());
                                    window.location.href = url.toString();
                                }} catch (e) {{
                                    console.error('❌ Graph: Direct navigation failed v{timestamp}:', e);
                                }}
                            }}
                            
                            console.log('🎯 Graph: Navigation request completed v{timestamp}')
                        }} else {{
                            console.log('🖱️ Double-click detected but no nodes selected v{timestamp}');
                        }}
                    }});
                    
                    // Also log single clicks for additional debugging
                    window.network.on("click", function (params) {{
                        if (params.nodes.length > 0) {{
                            const nodeId = params.nodes[0];
                            const nodeData = window.network.body.data.nodes.get(nodeId);
                            console.log('🖱️ Single-click on node v{timestamp}:', nodeId, '| Label:', nodeData ? nodeData.label : 'Unknown');
                        }}
                    }});
                    
                    // Log when hovering over nodes
                    window.network.on("hoverNode", function (params) {{
                        const nodeId = params.node;
                        const nodeData = window.network.body.data.nodes.get(nodeId);
                        console.log('🖱️ Hovering over node v{timestamp}:', nodeId, '| Label:', nodeData ? nodeData.label : 'Unknown');
                    }});
                    
                    console.log('✅ Enhanced double-click navigation and logging enabled v{timestamp}');
                    console.log('💡 Double-click any node to see detailed logging information v{timestamp}');
                }} else {{
                    console.log('⚠️ Network not found, retrying... v{timestamp}');
                    // Retry after a longer delay
                    setTimeout(arguments.callee, 1000);
                }}
            }}, 500);
        }});
        </script>
        """
        return navigation_js
    
    def _draw_colored_edges(self, G: nx.Graph, pos: Dict):
        """Draw edges with different colors based on relationship type."""
        edge_colors = {
            'sense': '#666666',
            'hypernym': '#FF4444',
            'hyponym': '#4488FF',
            'meronym': '#44AA44',
            'holonym': '#FFAA00'
        }
        
        # Group edges by relationship type
        edges_by_type = {}
        for source, target, data in G.edges(data=True):
            relation = data.get('relation', 'unknown')
            if relation not in edges_by_type:
                edges_by_type[relation] = []
            edges_by_type[relation].append((source, target))
        
        # Draw each group with its color
        for relation, edges in edges_by_type.items():
            color = edge_colors.get(relation, '#888888')
            nx.draw_networkx_edges(G, pos, edgelist=edges, 
                                 edge_color=color, width=2, alpha=0.7) 