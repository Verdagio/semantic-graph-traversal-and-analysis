from langchain_core.prompts import PromptTemplate

output_template = """
# Graph Analysis Report

### User Context:
**User Phrase/Terms:** {user_context}

### Graph Overview:
- **Overall Theme of the Graph:** {graph_theme}
- **Key concepts:** {key_concepts_in_graph}

### Relevance of Graph Elements to User Context:
{graph_elements_relevance}

### Semantic Traversal Results:

#### 1. Order of Visited Vertices:
{order} 

#### 2. Vertex Scores (Relevance to user context. Higher is better):
{scores}

#### 3. Best Path Analysis:
- **Best Path:** {best_path}
- **Best Score:** {best_score}
- **Why this Path was Chosen:**
  {best_path_reason}

#### 4. Other Viable Paths to best vertex:
{other_paths}

### Analysis of the best result:
{# for each vertex in the best_path}
#### Vertex ID: {vertex_id} {vertex_label} 
- **Score:** {vertex_score}
- **Path to Vertex:** {vertex_path}
- **Relevance to User Context:**
  {vertex_relevance}
- **Correctness Based on Graph and User Context:**
  {vertex_correctness}
- **Additional Notes:**
  {vertex_notes}
{# End for each vertex in the best_path}

### Insights:
**Relevance of Graph Elements:**
The elements of the graph are relevant to the user context because {explanation_of_relevance}. The vertices {relevant_vertices} directly align with the terms provided by the user, indicating a strong semantic relationship.

**Best Path Analysis:**
The best path was chosen based on the highest score of {best_score}, which reflects {best_path_strengths}. 
This path is particularly significant because {reason_for_significance}. 
Other paths, such as {other_paths_example}, were also considered but were not selected due to {reasons_for_not_selecting_other_paths}.

**Conclusion:**
{conclusion_summary}

**Recommendations:**
{recommendations_based_on_analysis}
"""


def get_default_system_prompt() -> str:
    return """
    Lets think step by step. 

    TASK:
    You are an expert data analyst tasked with analyzing graphs.
    Your goal is to evaluate a given graph and its chosen best path based on various criteria such as syntax, semantics, discourse, and pragmatics. 
    Additionally, you will assess correctness, relevance, and identify outliers.
    Your analysis should be thorough and objective, providing clear reasoning for your conclusions.
    Use labels instead of ids for readability unless using the id is specified by {vertex_id}

    
    You should respond with a detailed report using this format:
    
    """ + output_template


def get_default_prompt_template() -> PromptTemplate:
    return PromptTemplate(template="""
        CONTEXT:
        You are provided with the following graph:
        {total_graph}

        User context:
        {user_provided_context}
        
        Starting from the vertex with the ID {start_vertex_id},
        
        The order of visited vertices.
        {order}
        
        A dictionary mapping vertex IDs to their corresponding scores.
        {scores}
        
        The path leading to the vertex with the highest score.
        {best_path}
        
        The score of the vertex with the highest score.
        {best_score}
        
        A dictionary mapping vertex IDs to their corresponding paths.
        {paths}
    """
                                        )
