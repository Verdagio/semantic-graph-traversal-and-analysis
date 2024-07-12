
import hashlib
import json
import networkx as nx
import matplotlib.pyplot as plt


class Vertex:
    def __init__(self, properties):
        self.id = properties.pop('id')
        self.properties = properties
        self.edges = []

    def __repr__(self):
        return f"Vertex(id={self.id}, properties={self.properties})"

    def get_edges(self, edgesdf):
        edges = edgesdf.query(f"source == @self.id | target == @self.id")
        self.edges = set(edges['id'].values.tolist())
        return edges


class Edge:
    def __init__(self, properties):
        self.id = properties['id']
        self.source = properties['source']
        self.target = properties['target']
        self.label = properties['label']

    def __repr__(self):
        return f"Edge(id={self.id}, source={self.source}, target={self.target}, label={self.label})"


class Graph:
    def __init__(self):
        """
        Initializes the Graph object.

        This method initializes the Graph object by creating empty dictionaries for vertices, edges, and adjacency_list.

        Parameters:
            None

        Returns:
            None
        """
        self.vertices = {}
        self.edges = {}
        self.adjacency_list = {}

    def add_vertex(self, properties):
        """
        Adds a vertex to the graph if it does not already exist.

        Parameters:
            properties (dict): A dictionary containing the properties of the vertex.

        Returns:
            str: The ID of the added vertex.

        Raises:
            None.
        """
        if properties['id'] not in self.vertices:
            vertex = Vertex(properties)
            self.vertices[vertex.id] = vertex
            self.adjacency_list[vertex.id] = []
            return vertex.id

    def add_edge(self, edge_properties):
        """
        Adds an edge to the graph based on the given edge properties.

        Parameters:
            edge_properties (dict): A dictionary containing properties of the edge, including 'id', 'source', and 'target'.

        Returns:
            str: The id of the newly added edge.
        """
        if edge_properties['id'] not in self.edges:
            if edge_properties['source'] in self.vertices and edge_properties['target'] in self.vertices:
                source_id = edge_properties['source']
                target_id = edge_properties['target']
                if source_id not in self.vertices or target_id not in self.vertices:
                    raise ValueError(
                        "Both source and target vertices must exist in the graph.")
                edge = Edge(edge_properties)
                self.edges[edge.id] = edge
                self.adjacency_list[source_id].append((target_id, edge.id))
                return edge.id

    def get_vertex(self, vertex_id):
        """
        Retrieves a vertex from the graph based on the given vertex ID.

        Parameters:
            vertex_id (str): The ID of the vertex to retrieve.

        Returns:
            Vertex: The vertex corresponding to the provided ID.
        """
        return self.vertices[vertex_id]

    def __repr__(self):
        return f"Graph(vertices={self.vertices}, edges={self.edges})"

    def __to_networkx(self):
        """
        Converts the graph object to a NetworkX DiGraph.

        Returns:
            nx.DiGraph: A NetworkX DiGraph representing the graph.
        """
        G = nx.DiGraph()
        for vertex_id, vertex in self.vertices.items():
            G.add_node(vertex_id, **vertex.properties)
        for edge_id, edge in self.edges.items():
            G.add_edge(edge.source, edge.target, label=edge.label)
        return G

    def visualize(self):
        """
        Visualizes the graph using NetworkX.

        Parameters:
            self (Graph): The graph object.

        Returns:
            None
        """
        G = self.__to_networkx()

        G = G.subgraph([n for n, data in G.nodes(data=True)
                       if data.get('entity') is not None])

        entities = list(set([v.properties.get('entity')
                        for v in self.vertices.values()]))
        print(entities)
        node_colors = {'Actor': 'skyblue',
                       'Director': 'lightgreen', 'Movie': 'lightcoral'}
        colors = [node_colors[data.get('entity')] for n, data in G.nodes(
            data=True) if data.get('entity') is not None]

        plt.figure(figsize=(19.2, 10.8))

        labels = {node: data.get('label', node)
                  for node, data in G.nodes(data=True)}
        pos = nx.spring_layout(G, k=5)
        nx.draw(G, pos, with_labels=True, font_weight='bold', node_color=colors,
                node_size=4000, font_size=8, edge_color='gray', labels=labels)

        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_weight='bold', font_color='black', font_size=8)

        nx.draw_networkx_edges(G, pos, edge_color='gray')
        plt.show()

    def get_hash(self):
        """
        Creates a hash of the string representation of the graph.

        Args:
            graph (Graph): The graph object to create a hash from.

        Returns:
            str: A hash of the string representation of the graph.
        """
        return hashlib.sha256(self.__repr__().encode()).hexdigest()


def convert_to_jsonld(graph, ontology={"entity": "https://schema.org/Thing"}, save_as_jsonld=False, file_name='my-graph'):
    """
    Converts a graph to a JSON-LD object.

    Args:
        graph (Graph): The graph object to convert.

        onthology (dict): A dictionary mapping entity types to their respective URIs.

        onthology (dict, optional): A dictionary mapping entity types to their respective URIs, e.g.:
        {
            "Movie": "https://schema.org/Movie",
            "Actor": "https://schema.org/Actor",
            "Director": "https://schema.org/Director"
        }
        Defaults to { "entity": "https://schema.org/Thing" }.

        save_as_jsonld (bool, optional): Whether to save the JSON-LD object as a file. Defaults to False.

        file_name (str, optional): The name of the file to save the JSON-LD object as. Defaults to 'my-graph'. 

    Returns:
        dict: The JSON-LD object.
    """
    jsonld_data = {
        "@context": ontology,
        "@graph": []
    }

    for vertex_id, vertex in graph.vertices.items():
        jsonld_node = {"@id": vertex_id,
                       "@type": vertex.properties.get('entity')}
        for key, value in vertex.properties.items():
            if key != 'id' and key != 'entity':
                jsonld_node[key] = value
        jsonld_data['@graph'].append(jsonld_node)

    for edge_id, edge in graph.edges.items():
        for node in jsonld_data["@graph"]:
            if node["@id"] == edge.source:
                if edge.label not in node:
                    node[edge.label[:10]] = []
                node[edge.label[:10]].append({"@id": edge.target})

    if save_as_jsonld:
        with open(f'../data/graphs/{file_name}.json', 'w') as json_file:
            json.dump(jsonld_data, json_file, indent=2)

    return jsonld_data


if __name__ == "__main__":
    graph = Graph()
    vertices = [
        {'id': 'A', 'label': 'Node A', 'entity': 'Movie',
            'description': 'A informational piece about the landmarks of Irelands wild atlantic way'},
        {'id': 'B', 'label': 'Node B', 'entity': 'Movie',
            'description': 'A documentary about the west coast of Ireland’s wildlife'}
    ]

    edges = [
        {'id': '1', 'source': 'A', 'target': 'B', 'label': 'AB'},
    ]

    for vertex in vertices:
        graph.add_vertex(vertex)

    for edge in edges:
        graph.add_edge(edge)

    print(graph)
