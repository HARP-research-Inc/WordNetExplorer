"""
Visualization service for creating interactive graph visualizations.
"""

from typing import Optional, Tuple
from pyvis.network import Network
from src.models.graph_data import GraphData
from src.models.settings import VisualizationSettings
from src.graph.node_builder import NodeBuilder
from src.graph.edge_builder import EdgeBuilder
from src.graph.html_generator import GraphHTMLGenerator
from src.wordnet_explorer import visualize_graph as legacy_visualize


class VisualizationService:
    """Service for creating graph visualizations."""
    
    def __init__(self):
        """Initialize the visualization service."""
        self.html_generator = GraphHTMLGenerator()
    
    def visualize_graph(self, graph_data: GraphData, 
                       visualization_settings: VisualizationSettings) -> Tuple[Optional[Network], Optional[str]]:
        """
        Create an interactive visualization of the graph.
        
        Args:
            graph_data: The graph data to visualize
            visualization_settings: Visualization settings
            
        Returns:
            Tuple of (Network object, HTML string)
        """
        # For backward compatibility, use legacy visualizer
        settings_dict = visualization_settings.__dict__.copy()
        settings_dict['show_labels'] = visualization_settings.show_labels
        settings_dict['color_scheme'] = visualization_settings.color_scheme
        settings_dict['node_size_multiplier'] = visualization_settings.node_size_multiplier
        settings_dict['edge_width'] = visualization_settings.edge_width
        settings_dict['enable_physics'] = visualization_settings.enable_physics
        settings_dict['spring_strength'] = visualization_settings.spring_strength
        settings_dict['central_gravity'] = visualization_settings.central_gravity
        settings_dict['layout_type'] = visualization_settings.layout_type
        
        # Get tuple for legacy function
        G, node_labels = graph_data.to_tuple()
        
        return legacy_visualize(G, node_labels, settings_dict)
    
    def visualize_oop_graph(self, graph_data: GraphData,
                           visualization_settings: VisualizationSettings) -> Tuple[Optional[Network], Optional[str]]:
        """
        Create visualization using the new OOP approach.
        
        Args:
            graph_data: The graph data to visualize
            visualization_settings: Visualization settings
            
        Returns:
            Tuple of (Network object, HTML string)
        """
        if graph_data.num_nodes == 0:
            return None, None
        
        # Create builders
        node_builder = NodeBuilder(
            color_scheme=visualization_settings.color_scheme,
            size_multiplier=visualization_settings.node_size_multiplier
        )
        edge_builder = EdgeBuilder(edge_width=visualization_settings.edge_width)
        
        # Create network
        net = self._create_network(visualization_settings)
        
        # Add nodes
        for node_id in graph_data.graph.nodes():
            node_data = graph_data.get_node_data(node_id)
            if node_data:
                config = node_builder.build_node_config(
                    node_id=node_id,
                    node_data=node_data.to_dict(),
                    node_labels=graph_data.node_labels,
                    show_labels=visualization_settings.show_labels
                )
                net.add_node(node_id, **config)
        
        # Add edges
        for source, target in graph_data.graph.edges():
            edge_data = graph_data.get_edge_data(source, target)
            if edge_data:
                config = edge_builder.build_edge_config(
                    source=source,
                    target=target,
                    edge_data=edge_data.to_dict()
                )
                # Extract actual source and target from config
                actual_source = config.pop('source')
                actual_target = config.pop('target')
                net.add_edge(actual_source, actual_target, **config)
        
        # Apply layout
        self._apply_layout(net, visualization_settings.layout_type)
        
        # Generate HTML
        html_content = self.html_generator.save_network_to_html(net, inject_js=True)
        
        return net, html_content
    
    def _create_network(self, settings: VisualizationSettings) -> Network:
        """Create a pyvis Network with the specified settings."""
        net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black")
        
        # Set physics options
        if settings.enable_physics:
            net.force_atlas_2based(
                gravity=-50,
                central_gravity=settings.central_gravity,
                spring_length=100,
                spring_strength=settings.spring_strength,
                damping=0.09,
                overlap=0
            )
        else:
            net.toggle_physics(False)
        
        # Set interaction options
        net.set_options("""
        var options = {
            "interaction": {
                "hover": true,
                "tooltipDelay": 300,
                "zoomView": true,
                "dragView": true
            },
            "nodes": {
                "font": {
                    "size": 16
                }
            }
        }
        """)
        
        return net
    
    def _apply_layout(self, net: Network, layout_type: str) -> None:
        """Apply the specified layout to the network."""
        if layout_type == "Hierarchical":
            net.set_options("""
            var options = {
                "layout": {
                    "hierarchical": {
                        "enabled": true,
                        "direction": "UD",
                        "sortMethod": "directed",
                        "nodeSpacing": 200,
                        "levelSeparation": 150
                    }
                }
            }
            """)
        elif layout_type == "Circular":
            # Pyvis doesn't have built-in circular layout, but we can approximate
            net.barnes_hut(gravity=-8000, overlap=1)
        elif layout_type == "Grid":
            # Grid layout not directly supported in pyvis
            net.repulsion(node_distance=200, spring_length=100)
        # else: use default force-directed layout 