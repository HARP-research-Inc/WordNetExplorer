"""
HTML and JavaScript generation for graph visualizations.
"""

from typing import Optional
from pyvis.network import Network


class GraphHTMLGenerator:
    """Handles HTML and JavaScript generation for graph visualizations."""
    
    @staticmethod
    def inject_navigation_js(html_content: str) -> str:
        """Inject navigation JavaScript into HTML content."""
        navigation_js = GraphHTMLGenerator.get_navigation_js()
        return html_content.replace('</body>', navigation_js + '</body>')
    
    @staticmethod
    def get_navigation_js() -> str:
        """Get JavaScript for double-click navigation with enhanced console logging."""
        return """
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
                    setTimeout(arguments.callee, 100000);
                }
            }, 500);
        });
        </script>
        """
    
    @staticmethod
    def generate_physics_options(enable_physics: bool, spring_strength: float, central_gravity: float) -> str:
        """Generate physics configuration options for the network."""
        if enable_physics:
            return f"""
            var options = {{
              "physics": {{
                "enabled": true,
                "stabilization": {{"iterations": 100}},
                "barnesHut": {{
                  "gravitationalConstant": -8000,
                  "centralGravity": {central_gravity},
                  "springLength": 95,
                  "springConstant": {spring_strength},
                  "damping": 0.09
                }}
              }}
            }}
            """
        else:
            return """
            var options = {
              "physics": {"enabled": false}
            }
            """
    
    @staticmethod
    def save_network_to_html(net: Network, save_path: Optional[str] = None, 
                           inject_js: bool = True) -> str:
        """
        Save network to HTML with optional JavaScript injection.
        
        Args:
            net: The pyvis Network object
            save_path: Path to save the HTML file (optional)
            inject_js: Whether to inject navigation JavaScript
            
        Returns:
            HTML content as string
        """
        import tempfile
        import os
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        temp_file.close()
        
        try:
            # Save network to temp file
            net.save_graph(temp_file.name)
            
            # Read the HTML
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Inject JavaScript if requested
            if inject_js:
                html_content = GraphHTMLGenerator.inject_navigation_js(html_content)
            
            # Save to final path if provided
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            return html_content
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except (PermissionError, FileNotFoundError):
                pass 