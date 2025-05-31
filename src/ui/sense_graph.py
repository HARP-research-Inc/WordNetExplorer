"""
Sense similarity graph visualization module.
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional
import pandas as pd
from matplotlib.patches import Circle
import matplotlib.patches as mpatches

# Import the SenseScore from our service
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.services.sense_similarity import SenseScore


def create_2d_scatter_plot(word: str, sense_scores: List[SenseScore], settings: Dict):
    """Create a 2D scatter plot showing definition vs context similarity."""
    
    # Filter scores based on settings
    filtered_scores = []
    for score in sense_scores[:settings['show_top_n']]:
        if score.max_score >= settings['min_score']:
            filtered_scores.append(score)
    
    if not filtered_scores:
        st.info("No senses meet the minimum similarity threshold.")
        return None
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Set up the axes
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel('Definition Similarity →', fontsize=14)
    ax.set_ylabel('Context Similarity →', fontsize=14)
    ax.set_title(f'Sense Similarity Space for "{word}"', fontsize=16, fontweight='bold')
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add diagonal lines for combined score references
    for score in [0.2, 0.4, 0.6, 0.8]:
        x = np.linspace(0, score, 100)
        y = np.sqrt(score**2 - x**2)
        ax.plot(x, y, 'k--', alpha=0.2, linewidth=0.5)
        # Add label
        if score == 0.8:
            ax.text(score*0.7, score*0.7, f'{score:.1f}', fontsize=8, alpha=0.5, rotation=45)
    
    # Plot each sense
    colors = plt.get_cmap('viridis')(np.linspace(0, 1, len(filtered_scores)))
    
    for i, score in enumerate(filtered_scores):
        sense_num = score.synset_name.split('.')[-1].lstrip('0')
        
        # Get coordinates
        x = score.definition_score if score.definition_score is not None else 0
        y = score.context_score if score.context_score is not None else 0
        
        # Calculate combined score (distance from origin)
        combined = np.sqrt(x**2 + y**2) / np.sqrt(2)  # Normalize to 0-1
        
        # Plot point
        ax.scatter(x, y, s=200 + combined*300, c=[colors[i]], alpha=0.7, edgecolors='black', linewidth=2)
        
        # Add label
        ax.annotate(f'S{sense_num}', (x, y), xytext=(5, 5), textcoords='offset points', 
                   fontsize=12, fontweight='bold')
        
        # Draw line from origin
        ax.plot([0, x], [0, y], color=colors[i], alpha=0.3, linewidth=2)
    
    # Add legend with sense descriptions
    legend_elements = []
    for i, score in enumerate(filtered_scores):
        sense_num = score.synset_name.split('.')[-1].lstrip('0')
        def_score = score.definition_score if score.definition_score is not None else 0
        ctx_score = score.context_score if score.context_score is not None else 0
        combined = np.sqrt(def_score**2 + ctx_score**2) / np.sqrt(2)
        
        label = f'S{sense_num}: {score.definition[:30]}... (Combined: {combined:.3f})'
        legend_elements.append(mpatches.Patch(color=colors[i], label=label))
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
    
    # Add target zone
    target_circle = Circle((1, 1), 0.1, fill=False, edgecolor='green', linewidth=2, linestyle='--')
    ax.add_patch(target_circle)
    ax.text(0.95, 0.95, 'Best\nMatch', fontsize=10, ha='center', va='center', color='green')
    
    plt.tight_layout()
    return fig


def create_radar_chart(word: str, sense_scores: List[SenseScore], settings: Dict):
    """Create a radar chart showing all similarity scores."""
    
    # Filter scores based on settings
    filtered_scores = []
    for score in sense_scores[:settings['show_top_n']]:
        if score.max_score >= settings['min_score']:
            filtered_scores.append(score)
    
    if not filtered_scores:
        st.info("No senses meet the minimum similarity threshold.")
        return None
    
    # Set up the categories (one for each sense)
    categories = []
    for score in filtered_scores:
        sense_num = score.synset_name.split('.')[-1].lstrip('0')
        # Truncate definition for cleaner labels
        short_def = score.definition[:25] + '...' if len(score.definition) > 25 else score.definition
        categories.append(f'Sense {sense_num}\n{short_def}')
    
    # Number of variables (senses)
    N = len(categories)
    
    # Compute angle for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the circle
    
    # Initialize the plot
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Draw one axis per variable and add labels
    plt.xticks(angles[:-1], categories, size=10)
    
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0"], size=10)
    plt.ylim(0, 1)
    
    # Prepare data for each similarity type
    if settings['use_definition']:
        def_values = []
        for score in filtered_scores:
            def_values.append(score.definition_score if score.definition_score is not None else 0)
        def_values += def_values[:1]  # Complete the circle
        
        # Plot definition similarity
        ax.plot(angles, def_values, 'o-', linewidth=2, label='Definition Similarity', 
                color='green', markersize=8)
        ax.fill(angles, def_values, alpha=0.25, color='green')
    
    if settings['use_context']:
        ctx_values = []
        for score in filtered_scores:
            ctx_values.append(score.context_score if score.context_score is not None else 0)
        ctx_values += ctx_values[:1]  # Complete the circle
        
        # Plot context similarity
        ax.plot(angles, ctx_values, 'o-', linewidth=2, label='Context Similarity', 
                color='blue', markersize=8)
        ax.fill(angles, ctx_values, alpha=0.25, color='blue')
    
    if settings['use_definition'] and settings['use_context']:
        combined_values = []
        for score in filtered_scores:
            def_score = score.definition_score if score.definition_score is not None else 0
            ctx_score = score.context_score if score.context_score is not None else 0
            combined = np.sqrt(def_score**2 + ctx_score**2) / np.sqrt(2)
            combined_values.append(combined)
        combined_values += combined_values[:1]  # Complete the circle
        
        # Plot combined score
        ax.plot(angles, combined_values, 'o-', linewidth=2, label='Combined Score', 
                color='purple', markersize=8)
        ax.fill(angles, combined_values, alpha=0.25, color='purple')
    
    # Add legend
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
    
    # Add title
    plt.title(f'Sense Similarity Radar for "{word}"', size=16, fontweight='bold', pad=20)
    
    # Add grid
    ax.grid(True, alpha=0.5, linestyle='--')
    
    # Wrap long labels
    ax.tick_params(axis='x', pad=10)
    
    return fig


def create_bar_chart(word: str, sense_scores: List[SenseScore], settings: Dict):
    """Create a grouped bar chart showing similarity scores."""
    
    # Filter scores based on settings
    filtered_scores = []
    for score in sense_scores[:settings['show_top_n']]:
        if score.max_score >= settings['min_score']:
            filtered_scores.append(score)
    
    if not filtered_scores:
        st.info("No senses meet the minimum similarity threshold.")
        return None
    
    # Prepare data
    sense_labels = []
    def_scores = []
    ctx_scores = []
    combined_scores = []
    
    for score in filtered_scores:
        sense_num = score.synset_name.split('.')[-1].lstrip('0')
        sense_labels.append(f'Sense {sense_num}')
        
        def_score = score.definition_score if score.definition_score is not None else 0
        ctx_score = score.context_score if score.context_score is not None else 0
        
        def_scores.append(def_score)
        ctx_scores.append(ctx_score)
        combined_scores.append(np.sqrt(def_score**2 + ctx_score**2) / np.sqrt(2))
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(sense_labels))
    width = 0.25
    
    # Create bars
    if settings['use_definition']:
        bars1 = ax.bar(x - width, def_scores, width, label='Definition', color='green', alpha=0.8)
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{height:.3f}', ha='center', va='bottom', fontsize=10)
    
    if settings['use_context']:
        bars2 = ax.bar(x, ctx_scores, width, label='Context', color='blue', alpha=0.8)
        # Add value labels on bars
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{height:.3f}', ha='center', va='bottom', fontsize=10)
    
    if settings['use_definition'] and settings['use_context']:
        bars3 = ax.bar(x + width, combined_scores, width, label='Combined', color='purple', alpha=0.8)
        # Add value labels on bars
        for bar in bars3:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{height:.3f}', ha='center', va='bottom', fontsize=10)
    
    # Customize the plot
    ax.set_xlabel('Word Senses', fontsize=14)
    ax.set_ylabel('Similarity Score', fontsize=14)
    ax.set_title(f'Similarity Scores for "{word}"', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(sense_labels)
    ax.legend()
    ax.grid(True, axis='y', alpha=0.3)
    ax.set_ylim(0, 1.1)
    
    # Add sense definitions below x-axis
    for i, score in enumerate(filtered_scores):
        ax.text(i, -0.15, score.definition[:40] + '...', 
               ha='center', va='top', fontsize=8, rotation=15, transform=ax.get_xaxis_transform())
    
    plt.tight_layout()
    return fig


def render_sense_graph_visualization(
    word: str,
    sense_scores: List[SenseScore],
    settings: Dict
):
    """Render the sense similarity visualization."""
    
    if not sense_scores:
        st.info("No senses found for the given word.")
        return
    
    # Let user choose visualization type
    viz_type = st.radio(
        "Choose visualization type:",
        ["2D Scatter Plot", "Radar Chart", "Bar Chart"],
        horizontal=True,
        help="Different ways to visualize the similarity scores"
    )
    
    # Create the appropriate visualization
    if viz_type == "2D Scatter Plot":
        if not (settings['use_definition'] and settings['use_context']):
            st.warning("2D Scatter Plot requires both Definition and Context scoring to be enabled.")
            return
        fig = create_2d_scatter_plot(word, sense_scores, settings)
    elif viz_type == "Radar Chart":
        fig = create_radar_chart(word, sense_scores, settings)
    else:  # Bar Chart
        fig = create_bar_chart(word, sense_scores, settings)
    
    if fig:
        st.pyplot(fig)
        plt.close()
    
    # Display detailed scores
    with st.expander("📋 Detailed Scores", expanded=False):
        # Create a dataframe for better display
        data = []
        for score in sense_scores[:settings['show_top_n']]:
            if score.max_score >= settings['min_score']:
                sense_num = score.synset_name.split('.')[-1].lstrip('0')
                data.append({
                    'Sense': f"Sense {sense_num}",
                    'Definition': score.definition[:60] + '...',
                    'Def Score': f"{score.definition_score:.3f}" if score.definition_score is not None else "N/A",
                    'Ctx Score': f"{score.context_score:.3f}" if score.context_score is not None else "N/A",
                    'Combined': f"{score.combined_score:.3f}" if score.combined_score is not None else "N/A"
                })
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        
    # Display interpretation guide
    with st.expander("📊 How to Interpret", expanded=False):
        if viz_type == "2D Scatter Plot":
            st.markdown("""
            **2D Scatter Plot Guide:**
            - **X-axis**: Definition similarity (how well your definition matches)
            - **Y-axis**: Context similarity (how well your context sentence matches)
            - **Point size**: Larger points have higher combined scores
            - **Best matches**: Closer to the top-right corner (1,1)
            - **Lines from origin**: Show the "pull" of each sense
            - **Diagonal curves**: Show lines of equal combined score
            """)
        elif viz_type == "Radar Chart":
            st.markdown("""
            **Radar Chart Guide:**
            - Each **axis** represents a different sense of the word
            - **Colored lines** show different similarity metrics:
              - 🟢 **Green line**: Definition similarity scores
              - 🔵 **Blue line**: Context similarity scores  
              - 🟣 **Purple line**: Combined scores (if both metrics are enabled)
            - **Higher values** (further from center): Better match for that sense
            - **Peak points**: The sense(s) where each line reaches furthest indicate the best matches
            - **Compare lines**: See which similarity metric best identifies your intended sense
            """)
        else:  # Bar Chart
            st.markdown("""
            **Bar Chart Guide:**
            - **Green bars**: Definition similarity scores
            - **Blue bars**: Context similarity scores
            - **Purple bars**: Combined scores (average of both)
            - **Higher bars**: Better matches
            - **Definitions**: Shown below each sense number
            """) 