"""
Example of using the new OOP architecture for WordNet Explorer.
"""

from src.models.settings import AppSettings, ExplorationSettings, VisualizationSettings, RelationshipSettings
from src.models.graph_data import GraphData, NodeType
from src.services import WordNetService, GraphService, VisualizationService


def main():
    """Example of using the OOP-based WordNet Explorer."""
    
    # 1. Create settings using data classes
    settings = AppSettings(
        exploration=ExplorationSettings(
            word="dog",
            depth=2,
            max_nodes=50,
            max_branches=3,
            pos_filter=["Nouns", "Verbs"]
        ),
        visualization=VisualizationSettings(
            color_scheme="Vibrant",
            node_size_multiplier=1.5,
            enable_physics=True,
            show_labels=True
        ),
        relationships=RelationshipSettings(
            show_hypernym=True,
            show_hyponym=True,
            show_meronym=True
        )
    )
    
    # 2. Validate settings
    errors = settings.validate()
    if errors:
        print("Settings validation errors:")
        for error in errors:
            print(f"  - {error}")
        return
    
    # 3. Create services
    wordnet_service = WordNetService()
    graph_service = GraphService(wordnet_service)
    viz_service = VisualizationService()
    
    # 4. Get word information
    word_info = wordnet_service.get_word_info("dog")
    print(f"Found {word_info.total_senses} senses for '{word_info.word}':")
    for synset in word_info.synsets:
        print(f"  - {synset.get_formatted_label()}: {synset.definition}")
    
    # 5. Build the graph
    graph_data = graph_service.build_graph(settings)
    print(f"\nGraph created with {graph_data.num_nodes} nodes and {graph_data.num_edges} edges")
    
    # 6. Analyze graph structure
    main_nodes = graph_data.get_nodes_by_type(NodeType.MAIN)
    print(f"Main nodes: {len(main_nodes)}")
    
    synset_nodes = graph_data.get_nodes_by_type(NodeType.SYNSET)
    print(f"Synset nodes: {len(synset_nodes)}")
    
    # 7. Create visualization
    net, html = viz_service.visualize_graph(graph_data, settings.visualization)
    if html:
        print("\nVisualization created successfully!")
        # Save to file
        with open("example_graph.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved to example_graph.html")
    
    # 8. Example of navigation context
    from src.models.word_data import NavigationContext
    
    nav_context = NavigationContext(current_word="dog")
    nav_context.navigate_to("cat")
    nav_context.navigate_to("animal")
    
    print(f"\nNavigation history: {nav_context.navigation_history}")
    print(f"Current word: {nav_context.current_word}")
    print(f"Breadcrumb path: {nav_context.get_breadcrumb_path()}")


def example_backward_compatibility():
    """Example showing backward compatibility with dictionary-based approach."""
    
    # Old dictionary-based settings
    old_settings = {
        'word': 'tree',
        'depth': 2,
        'max_nodes': 30,
        'show_hypernym': True,
        'show_hyponym': True,
        'color_scheme': 'Pastel',
        'node_size_multiplier': 1.2
    }
    
    # Convert to new OOP settings
    new_settings = AppSettings.from_dict(old_settings)
    
    # Use as before
    graph_service = GraphService()
    graph_data = graph_service.build_graph(new_settings)
    
    # Convert back to dictionary if needed
    settings_dict = new_settings.to_dict()
    print(f"Settings as dict: {settings_dict}")


def example_custom_graph_building():
    """Example of building a custom graph using the OOP models."""
    from src.models.graph_data import NodeData, EdgeData, EdgeType
    import networkx as nx
    
    # Create empty graph data
    graph_data = GraphData(graph=nx.Graph())
    
    # Add custom nodes
    main_node = NodeData(
        node_id="custom_main",
        node_type=NodeType.MAIN,
        label="CUSTOM",
        word="custom"
    )
    graph_data.add_node(main_node)
    
    # Add related nodes
    for i in range(3):
        node = NodeData(
            node_id=f"related_{i}",
            node_type=NodeType.WORD,
            label=f"Related {i}",
            word=f"related{i}"
        )
        graph_data.add_node(node)
        
        # Add edge
        edge = EdgeData(
            source="custom_main",
            target=f"related_{i}",
            edge_type=EdgeType.SIMILAR_TO,
            color="#4ECDC4"
        )
        graph_data.add_edge(edge)
    
    print(f"Custom graph: {graph_data.num_nodes} nodes, {graph_data.num_edges} edges")


if __name__ == "__main__":
    main()
    print("\n" + "="*50 + "\n")
    example_backward_compatibility()
    print("\n" + "="*50 + "\n")
    example_custom_graph_building() 