import datetime
import hashlib
from langchain_core.prompts import PromptTemplate

from app.lib.semantic_traversal import semantic_traversal
from app.lib.encoders import EmbModelName, embedding_model_provider
from app.lib.language_model import llm_provider
from app.lib.default_prompt import get_default_prompt_template
from app.lib.default_prompt import get_default_system_prompt
from app.lib.graph import Graph, convert_to_jsonld


class Analyser:

    def __init__(self, embedding_model_name: EmbModelName, llm_name, traversal_depreciation=0.05, traversal_min_score_threshold=0.1, embedding_model_variant=None):
        self.llm = llm_provider(llm_name)
        self.traversal_attrs = {
            'embedding_model': embedding_model_provider(embedding_model_name, embedding_model_variant),
            'depreciation': traversal_depreciation,
            'min_score_threshold': traversal_min_score_threshold
        }
        self.traversal_history = {}
        self.set_system_prompt(get_default_system_prompt())
        self.default_prompt = get_default_prompt_template()

    def set_traversal_params(self, depreciation, min_score_threshold):
        self.traversal_attrs['depreciation'] = depreciation
        self.traversal_attrs['min_score_threshold'] = min_score_threshold

    def set_system_prompt(self, system_prompt):
        self.llm.set_system_message(system_prompt)

    def set_default_prompt(self, template):
        self.default_prompt = PromptTemplate.from_template(template=template)

    def set_embedding_model(self, embedding_model: EmbModelName, embedding_model_variant):
        self.traversal_attrs['embedding_model'] = embedding_model_provider(
            embedding_model, embedding_model_variant)

    def set_llm(self, llm_name):
        self.llm = llm_provider(llm_name)

    def get_traversal_history(self):
        return self.traversal_history

    def get_current_config(self):
        print(self.traversal_attrs['embedding_model'].model_name)
        return {
            'llm_model_name': self.llm.model.model_name,
            'traversal_depreciation': self.traversal_attrs['depreciation'],
            'traversal_min_score_threshold': self.traversal_attrs['min_score_threshold'],
            'embedding_model_name': self.traversal_attrs['embedding_model'].model_name,
            'default_prompt_template': self.default_prompt.template,
            'system_message': self.llm.get_system_message()
        }

    def __to_graph(self, graph_data):
        graph = Graph()

        [graph.add_vertex(vertex) for vertex in graph_data['vertices']]
        [graph.add_edge(edge) for edge in graph_data['edges']]

        return graph

    def __traverse(self, graph: Graph, start_vertex_id, context):
        graph_hash = hashlib.sha256(graph.__repr__().encode()).hexdigest()

        embedding_model = self.traversal_attrs['embedding_model']
        depreciation = self.traversal_attrs['depreciation']
        min_score_threshold = self.traversal_attrs['min_score_threshold']

        if graph_hash not in self.traversal_history:
            order, scores, best_path, best_score, paths = semantic_traversal(
                graph=graph,
                start_vertex_id=start_vertex_id,
                context=context,
                embedding_model=embedding_model,
                depreciation=depreciation,
                min_score_threshold=min_score_threshold
            )

            self.traversal_history[graph_hash] = dict({
                'id': graph_hash,
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'order': order,
                'scores': scores,
                'best_path': best_path,
                'best_score': best_score,
                'paths': paths,
                'meta': {
                    'embedding_model': embedding_model._EmbeddingModel__encoder.model_name,
                    'depreciation': depreciation,
                    'min_score_threshold': min_score_threshold,
                    'graph': convert_to_jsonld(graph),
                    'start_vertex_id': start_vertex_id,
                    'context': context
                },
                'graph_analysis': ''
            })

        return self.traversal_history[graph_hash]

    def traverse(self, graph, start_vertex_id, context):
        if type(graph) != Graph:
            graph = self.__to_graph(graph)

        traversal_result = self.__traverse(graph, start_vertex_id, context)
        return traversal_result

    # TODO: Add support for ontologies to inject into jsonld
    def analyse(self, graph_data, start_vertex_id, context):
        traversal_result = self.traverse(graph_data, start_vertex_id, context)

        prompt = self.default_prompt.format(
            total_graph=traversal_result['meta']['graph'],
            user_provided_context=traversal_result['meta']['context'],
            start_vertex_id=traversal_result['meta']['start_vertex_id'],
            order=traversal_result['order'],
            scores=traversal_result['scores'],
            best_path=traversal_result['best_path'],
            best_score=traversal_result['best_score'],
            paths=traversal_result['paths']
        )

        response = self.llm.chat(prompt)

        self.traversal_history[traversal_result['id']
                               ]['graph_analysis'] = response

        return self.traversal_history[traversal_result['id']]

    def question(self, query):
        return self.llm.chat(query + "\n Instruction: Ignore the output template for this question. Just return the answer in markdown format.")


if __name__ == "__main__":
    analyst = Analyser(embedding_model_name='openai',
                       embedding_model_variant='text-embedding-3-small', llm_name='gpt-4o')

    graph_data = {
        "vertices": [
            {'id': 'A', 'label': 'Node A', 'entity': 'Movie',
                'description': 'A movie about horses in the wild west'},
            {'id': 'B', 'label': 'Node B', 'entity': 'Movie',
                'description': 'A documentary about the west coast of Ireland’s wildlife'},
            {'id': 'C', 'label': 'Node C', 'entity': 'Movie',
                'description': 'A documentary about the west gulfs of Iraq and Syria'},
            {'id': 'D', 'label': 'Node D', 'entity': 'Movie',
                'description': 'A documentary about the western seas of North America'},
            {'id': 'E', 'label': 'Node E', 'entity': 'Movie',
                'description': 'A movie about dogs and cats'},
            {'id': 'F', 'label': 'Node F', 'entity': 'Movie',
                'description': 'A movie about ancient Egypt'},
            {'id': 'G', 'label': 'Node G', 'entity': 'Movie',
                'description': 'A documentary about the Amazon rainforest'},
            {'id': 'H', 'label': 'Node H', 'entity': 'Movie',
                'description': 'A documentary about space exploration'},
            {'id': 'I', 'label': 'Node I', 'entity': 'Movie',
                'description': 'A movie about medieval knights'},
            {'id': 'J', 'label': 'Node J', 'entity': 'Movie',
                'description': 'A documentary about the Great Barrier Reef'},
            {'id': 'K', 'label': 'Node K', 'entity': 'Movie',
                'description': 'A documentary about the Sahara desert'},
        ],
        "edges": [
            {'id': '1', 'source': 'A', 'target': 'B', 'label': 'AB'},
            {'id': '2', 'source': 'A', 'target': 'C', 'label': 'AC'},
            {'id': '3', 'source': 'B', 'target': 'D', 'label': 'BD'},
            {'id': '4', 'source': 'C', 'target': 'D', 'label': 'CD'},
            {'id': '5', 'source': 'D', 'target': 'E', 'label': 'DE'},
            {'id': '6', 'source': 'A', 'target': 'F', 'label': 'AF'},
            {'id': '7', 'source': 'B', 'target': 'G', 'label': 'BG'},
            {'id': '8', 'source': 'C', 'target': 'H', 'label': 'CH'},
            {'id': '9', 'source': 'D', 'target': 'I', 'label': 'DI'},
            {'id': '10', 'source': 'E', 'target': 'J', 'label': 'EJ'},
            {'id': '11', 'source': 'F', 'target': 'G', 'label': 'FG'},
            {'id': '12', 'source': 'G', 'target': 'H', 'label': 'GH'},
            {'id': '13', 'source': 'H', 'target': 'I', 'label': 'HI'},
            {'id': '14', 'source': 'I', 'target': 'J', 'label': 'IJ'},
            {'id': '15', 'source': 'J', 'target': 'K', 'label': 'JK'},
            {'id': '16', 'source': 'K', 'target': 'A', 'label': 'KA'},
            {'id': '17', 'source': 'E', 'target': 'K', 'label': 'EK'},
            {'id': '18', 'source': 'F', 'target': 'H', 'label': 'FH'},
            {'id': '19', 'source': 'G', 'target': 'I', 'label': 'GI'},
            {'id': '20', 'source': 'J', 'target': 'A', 'label': 'JA'},
        ]
    }

    res = analyst.analyse(graph_data, 'A', 'pet animals')
    print(res)
    res = analyst.question('How many reference animals?')
    print(res)
    res = analyst.question('Are there any other interesting insights?')
    print(res)
    res = analyst.question(
        'Is there any indication of fictional vs factual content?')
    print(res)
