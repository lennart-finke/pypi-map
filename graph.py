"""
This file provides some simple Python functionality to plot a 
.gexf file after layout with e.g.Gephi.

For a d3.js version, see source of https://fi-le.net/pypi/
"""

import xml.etree.ElementTree as ET
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import json
import re

def parse_gexf(filename):
    """
    Efficiently parse a large GEXF file (100,000+ nodes).
    Extracts node positions and builds a directed graph.
    """
    tree = ET.parse(filename)
    root = tree.getroot()

    ns = {
        'gexf': 'http://gexf.net/1.3',
        'viz':  'http://gexf.net/1.3/viz'
    }
    
    G = nx.DiGraph()
    
    graph_elem = root.find('gexf:graph', ns)
    
    nodes_elem = graph_elem.find('gexf:nodes', ns)
    for node_elem in nodes_elem.findall('gexf:node', ns):
        node_id = node_elem.get('id')
        node_label = node_elem.get('label', node_id)

        pos_elem = node_elem.find('viz:position', ns)
        if pos_elem is not None:
            x = float(pos_elem.get('x', 0.0))
            y = float(pos_elem.get('y', 0.0))
        else:
            x, y = 0.0, 0.0

        G.add_node(node_id, label=node_label, pos=(x, y))
    
        
    edges_elem = graph_elem.find('gexf:edges', ns)
    for edge_elem in edges_elem.findall('gexf:edge', ns):
        source = edge_elem.get('source')
        target = edge_elem.get('target')
        G.add_edge(source, target)
    

    return G

def plot_graph_large(G):
    """
    Plots a large-scale graph with 100,000+ nodes using Plotly.
    - Uses WebGL (`Scattergl`) for fast rendering.
    - Only displays labels for high-degree nodes to reduce clutter.
    """
    # Extract node positions
    pos = {n: data['pos'] for n, data in G.nodes(data=True)}
    x_values = [pos[n][0] for n in G.nodes()]
    y_values = [pos[n][1] for n in G.nodes()]
    
    # Compute total degree (in + out) for scaling
    in_degrees = dict(G.in_degree())
    max_size = 100000
    min_size = 3
    node_sizes = [max(min_size, np.sqrt(in_degrees[n])) for n in G.nodes()]

    # Choose which nodes to label
    label_threshold = 150
    labels = [G.nodes[n]['label'] if in_degrees.get(n, 0) >= label_threshold else "" for n in G.nodes()]
    hover_labels = [f"<b>{G.nodes[n]['label']}</b><br><br>Child Packages: {in_degrees.get(n, 0)}<br><a href='https://pypi.org/project/{G.nodes[n]['label']}'>https://pypi.org/project/{G.nodes[n]['label']}</a>" for n in G.nodes()]

    # Create the scatter plot using WebGL (`Scattergl`)
    fig = go.Figure()

    # Sort nodes by size to control draw order
    sorted_indices = np.argsort(node_sizes)
    
    version_map = {}
    with open('deps_smol.jsonl') as f:
        for line in f:
            data = json.loads(line)
            if data.get('requires_python'):
                # Extract minimum version using regex
                match = re.search(r'>=(\d+\.\d+)', data['requires_python'])
                if match:
                    version_map[data['name']] = float(match.group(1))
    
    # Create color scale based on Python version
    node_colors = []
    for node in G.nodes():
        version = version_map.get(G.nodes[node]['label'], 3.0)  # default to 3.0
        node_colors.append(version)
    
    fig.add_trace(go.Scattergl(
        x=[x_values[i] for i in sorted_indices],
        y=[y_values[i] for i in sorted_indices],
        mode='markers+text',
        text=[labels[i] for i in sorted_indices],
        hovertext=[hover_labels[i] for i in sorted_indices],
        hoverinfo='text',
        textposition='middle center',
        textfont=dict(size=5, color='black'),
        marker=dict(
            size=[node_sizes[i] for i in sorted_indices],
            color=[node_colors[i] for i in sorted_indices],
            colorbar=dict(title="Min Python Version"),
            opacity=0.5
        )
    ))

    fig.update_layout(
        title="Large-Scale GEXF Graph (100,000+ Nodes)",
        xaxis=dict(visible=False, showgrid=False),
        yaxis=dict(visible=False, showgrid=False),
        showlegend=False,
        width=1200,
        height=800,
        # transparent background
        plot_bgcolor='rgba(0,0,0,0)',
    )

    fig.show()

if __name__ == "__main__":
    filename = "g.gexf"
    G = parse_gexf(filename)
    plot_graph_large(G)
