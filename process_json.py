import json
import re
import networkx as nx
from tqdm import tqdm

def parse_dependency_string(dep_str):
    """
    Given a string like:
        'requests (>=2.26.0) ; python_version >= "3.7"'
    or:
        'munch (>=2.1.1)'
    or:
        'pylint (<3.0,>=2.0) ; extra == "dev"'
    we want to extract just the base package name: 'requests', 'munch', 'pylint'.
    """
    # Split on version-indicating special characters and strip
    for char in ";(<>!~=":
        dep_str = dep_str.split(char, 1)[0].strip()
    
    
    # The first token should be the package name. E.g. "requests"
    # But it can also be 'Some-Pkg [extra]' in a few cases, so optionally
    # we remove any bracketed 'extras'
    dep_str = re.sub(r'\[.*?\]', '', dep_str)
    
    # Also, strip out any trailing characters
    dep_str = dep_str.strip().lower()
    
    # If something remains, that should be our dependency name
    return dep_str if dep_str else None

def build_dependency_graph(jsonl_path, max_lines=None):
    """
    Read lines from the JSONL file and build a directed graph
    of the dependencies.
    """
    G = nx.DiGraph()

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for i, line in tqdm(enumerate(f)):
            if max_lines and i >= max_lines:
                break
            
            record = json.loads(line)
            package_name = record.get("name").lower()
            deps = record["requires_dist"]

            if package_name:
                l = package_name.lower()
                if "cash" in l or "free" in l:
                    continue
                if len(deps) == 0:
                    continue
                if any(char.isdigit() for char in package_name):
                    continue
                #if random.random() < 0.9:
                #    continue
                G.add_node(package_name)

                for dep_str in deps:
                    dep_name = parse_dependency_string(dep_str)
                    if dep_name:
                        # add edge package_name -> dep_name
                        # (i.e. "this package depends on dep_name")
                        G.add_edge(package_name, dep_name)
    
    return G

if __name__ == "__main__":
    graph = build_dependency_graph("deps.jsonl", max_lines=None)
    # Get the connected component containing numpy
    numpy_component = nx.node_connected_component(nx.Graph(graph.to_undirected()), "numpy")
    # Create a new subgraph with only the numpy component
    graph = graph.subgraph(numpy_component)

    # Export the graph to a Gephi-readable format:
    nx.write_gexf(graph, "pypi_deps.gexf")
    # or
    # nx.write_graphml(graph, "pypi_deps.graphml")

    print("Graph building complete!")
    print(f"Number of nodes: {graph.number_of_nodes()}")
    print(f"Number of edges: {graph.number_of_edges()}")