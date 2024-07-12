# semantic-graph-traversal-and-analysis

## What it does:

This project introduces a semantic traversal algorithm that navigates a graph structure by leveraging an embedding model to assess and prioritize connections based on contextual relevance. Starting from an initial vertex, the algorithm computes semantic similarities between the context and verticies. It uses these similarities to guide the traversal, dynamically updating and depreciating the relevance scores to refine the exploration path. The aim of this approach is to demonstrate an efficient method for context-driven graph exploration, optimizing for meaningful data retrieval and analysis. Following traversal and scoring of the graph, a Large Language Model is used to analyse the data found and explain the results based off the original graph.

## Prequisites

1. PYTHON v 3.10.13
2. Patience...

## How to run:
### Local

1. Create a .env file and add the following parameters:
```
LLM_API_KEY=<api-key> (NEEDED FOR OPENAI models AND mistral-embed. Mistral llms are provided using ollama)
EMBEDDING_MODEL_NAME=<"mistral" | "bert" | "openai" | "sentence_transformer">
EMBEDDING_MODEL_VARIANT=<pick your poison e.g. 'text-embedding-ada-002'>
LLM_NAME=<llm of choice e.g. 'gpt-4o'>
```
2. `pip install -m requirements.txt`
3. `python -m nltk.downloader stopwords`
4. `uvicorn main:app --host localhost --port 8000`

### Docker

1. `docker build -t graph-analysis-assist .`
2. `docker-compose up --build`

## How to use:

The functionality is exposed over api endpoints which can be accessed using CURL, POSTMAN, etc etc.:

```
curl -X POST http://localhost:8000/api/v1/analyse/ \
-H "Content-Type: application/json" \
-d '{
    "graph_data": {
        "vertices": [
            {"id": "A", "label": "Node A", "entity": "Movie", "description": "A movie about horses in the wild west"},
            {"id": "B", "label": "Node B", "entity": "Movie", "description": "A documentary about the west coast of Ireland’s wildlife"},
            {"id": "C", "label": "Node C", "entity": "Movie", "description": "A documentary about the west gulfs of Iraq and Syria"},
            {"id": "D", "label": "Node D", "entity": "Movie", "description": "A documentary about the western seas of North America"},
            {"id": "E", "label": "Node E", "entity": "Movie", "description": "A movie about dogs and cats"},
            {"id": "F", "label": "Node F", "entity": "Movie", "description": "A movie about ancient Egypt"},
            {"id": "G", "label": "Node G", "entity": "Movie", "description": "A documentary about the Amazon rainforest"},
            {"id": "H", "label": "Node H", "entity": "Movie", "description": "A documentary about space exploration"},
            {"id": "I", "label": "Node I", "entity": "Movie", "description": "A movie about medieval knights"},
            {"id": "J", "label": "Node J", "entity": "Movie", "description": "A documentary about the Great Barrier Reef"},
            {"id": "K", "label": "Node K", "entity": "Movie", "description": "A documentary about the Sahara desert"}
        ],
        "edges": [
            {"id": "1", "source": "A", "target": "B", "label": "AB"},
            {"id": "2", "source": "A", "target": "C", "label": "AC"},
            {"id": "3", "source": "B", "target": "D", "label": "BD"},
            {"id": "4", "source": "C", "target": "D", "label": "CD"},
            {"id": "5", "source": "D", "target": "E", "label": "DE"},
            {"id": "6", "source": "A", "target": "F", "label": "AF"},
            {"id": "7", "source": "B", "target": "G", "label": "BG"},
            {"id": "8", "source": "C", "target": "H", "label": "CH"},
            {"id": "9", "source": "D", "target": "I", "label": "DI"},
            {"id": "10", "source": "E", "target": "J", "label": "EJ"},
            {"id": "11", "source": "F", "target": "G", "label": "FG"},
            {"id": "12", "source": "G", "target": "H", "label": "GH"},
            {"id": "13", "source": "H", "target": "I", "label": "HI"},
            {"id": "14", "source": "I", "target": "J", "label": "IJ"},
            {"id": "15", "source": "J", "target": "K", "label": "JK"},
            {"id": "16", "source": "K", "target": "A", "label": "KA"},
            {"id": "17", "source": "E", "target": "K", "label": "EK"},
            {"id": "18", "source": "F", "target": "H", "label": "FH"},
            {"id": "19", "source": "G", "target": "I", "label": "GI"},
            {"id": "20", "source": "J", "target": "A", "label": "JA"}
        ]
    },
    "start_vertex_id": "A",
    "context": "Pet animals"
}'
```