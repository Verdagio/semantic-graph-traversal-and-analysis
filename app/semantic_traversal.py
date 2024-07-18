import heapq

import numpy as np

from app.graph import Graph
from app.encoders import EmbeddingModel

def semantic_traversal(graph: Graph, embedding_model: EmbeddingModel, start_vertex_id: str, context: str, ignore_direction=False, depreciation=0.05, min_score_threshold=0.1) -> tuple:
    """
    Performs a semantic traversal on a graph using a given model and context.

    Args:
        graph (Graph): The graph to traverse.
        embedding_model (EmbeddingModel): The model used for encoding and similarity calculations.
        start_vertex_id (str): The ID of the starting vertex.
        context (str): The context used for encoding.
        depreciation (float, optional): The depreciation rate for updating the mean. Defaults to 0.05.
        min_score_threshold (float, optional): The minimum threshold for semantic scores. Defaults to 0.1.

    Returns:
        tuple: A tuple containing the following:

    """

    ctx_emb = embedding_model.encode(context)
    min_heap = [(0, start_vertex_id, [])]
    visited, order, scores, paths = set(), [], {}, {}
    
    if ignore_direction:
        incoming_edges = {v: [] for v in graph.adjacency_list}
        for vertex_id in graph.adjacency_list:
            for neighbor, _ in graph.adjacency_list[vertex_id]:
                incoming_edges[neighbor].append(vertex_id)

    while min_heap:
        neg_current_mean, vertex_id, path = heapq.heappop(min_heap)
        current_mean = -neg_current_mean
        if vertex_id not in visited:
            visited.add(vertex_id)
            order.append(vertex_id)
            path = path + [vertex_id]
            paths[vertex_id] = path
            scores[vertex_id] = current_mean.item() if isinstance(current_mean, np.ndarray) else current_mean
            next_verticies = []

            for neighbor, _ in graph.adjacency_list[vertex_id]: 
                if neighbor not in visited:
                    v = graph.get_vertex(neighbor)
                    vertex_emb = embedding_model.encode(str(v.properties))
                    semantic_score = embedding_model.similarity(ctx_emb, vertex_emb)
                    if semantic_score >= min_score_threshold:
                        next_verticies.append((neighbor, semantic_score))

            for neighbor, score in next_verticies:
                new_mean = current_mean + score * (1 - depreciation) 
                heapq.heappush(min_heap, (-new_mean, neighbor, path))
            
            if ignore_direction:
                for incoming in incoming_edges[vertex_id]:
                    if incoming not in visited:
                        v = graph.get_vertex(incoming)
                        vertex_emb = embedding_model.encode(str(v.properties))
                        semantic_score = embedding_model.similarity(ctx_emb, vertex_emb)
                        if semantic_score >= min_score_threshold:
                            new_mean = current_mean + semantic_score * (1 - depreciation)
                            heapq.heappush(min_heap, (-new_mean, incoming, path))

    best_vertex = max(scores, key=scores.get)
    best_path = paths[best_vertex]
    best_score = scores[best_vertex]

    return order, scores, best_path, best_score, paths

