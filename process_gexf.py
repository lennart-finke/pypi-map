import xml.etree.ElementTree as ET
import json
import networkx as nx

def parse_gexf(filename):
    """
    Parse a large GEXF file with precomputed positions.
    """
    tree = ET.parse(filename)
    root = tree.getroot()
    ns = {
        'gexf': 'http://gexf.net/1.3',
        'viz':  'http://gexf.net/1.3/viz'
    }
    G = nx.DiGraph()
    graph_elem = root.find('gexf:graph', ns)
    
    # Parse nodes
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
        G.add_node(node_id, label=node_label, x=x, y=y)
    
    # Parse edges (dependencies)
    edges_elem = graph_elem.find('gexf:edges', ns)
    for edge_elem in edges_elem.findall('gexf:edge', ns):
        source = edge_elem.get('source')
        target = edge_elem.get('target')
        G.add_edge(source, target)
    
    return G

def export_to_json(G, output_file):
    """
    Exports nodes with x,y and computed usage (in–degree)
    and the list of edges as JSON.
    """
    nodes = []
    for node, data in G.nodes(data=True):
        # Compute usage as in–degree
        usage = G.in_degree(node)
        nodes.append({
            "id": node,
            "label": data.get("label", node),
            "x": data.get("x", 0.0),
            "y": data.get("y", 0.0),
            "usage": usage
        })
    edges = []
    for source, target in G.edges():
        edges.append({"source": source, "target": target})
    
    data = {"nodes": nodes, "edges": edges}
    with open(output_file, "w") as f:
        json.dump(data, f)
        
if __name__ == "__main__":
    gexf_file = "g_big.gexf"         # your large GEXF file
    output_file = "pypi_data_big.json"
    G = parse_gexf(gexf_file)
    export_to_json(G, output_file)
