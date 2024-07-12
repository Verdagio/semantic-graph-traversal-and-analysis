import os
import numpy as np
import re
import nltk
import torch

from numpy.core.multiarray import array as array
import openai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from abc import ABC, abstractmethod
from transformers import BertTokenizer, BertModel
from mistralai.client import MistralClient
from dotenv import load_dotenv
from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return str(self.value)

class EmbModelName(StrEnum):
    Mistral = "mistral"
    Bert = "bert"
    OpenAI = "openai"
    SentenceTransformer = "sentence_transformer"

load_dotenv()
nltk.download('punkt')
    
class Encoder(ABC):
    @abstractmethod
    def encode(self, value) -> np.array:
        pass
    
class SentenceTransformenEncoder(Encoder):
    def __init__(self, model_name = 'all-MiniLM-L6-v2') -> None:
        super().__init__()
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
    
    def encode(self, value):
        emb = self.model.encode(value)
        return np.array(emb)

class OpenAIEncoder(Encoder):
    def __init__(self, model = 'text-embedding-ada-002') -> None:
        super().__init__()
        self.client = openai.OpenAI(api_key=str(os.getenv('LLM_API_KEY')))
        self.model_name = model

    def encode(self, value: str) -> np.ndarray:
        response = self.client.embeddings.create(
            input = value,
            model = self.model_name
        )
        return np.array(response.data[0].embedding)

    
class BertEncoder(Encoder):
    
    def __init__(self, model_name = 'bert-base-uncased') -> None:
        super().__init__()
        self.model_name = model_name
        self.__tokenizer = BertTokenizer.from_pretrained(model_name)
        self.__model = BertModel.from_pretrained(model_name)
        
    def encode(self, value):
        inputs = self.__tokenizer(value, return_tensors="pt")
        with torch.no_grad():
            outputs = self.__model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        return np.array(embeddings)[0]
    
class MistralEncoder(Encoder):
    def __init__(self, model = 'mistral-embed') -> None:
        super().__init__()
        self.__client = MistralClient(api_key=str(os.getenv('LLM_API_KEY')))
        self.model_name = model
    
    def encode(self, value) -> np.array:
        embeddings_batch_response = self.__client.embeddings(
            model = self.model_name,
            input = [value],
        )
    
        return embeddings_batch_response.data[0].embedding
    
class EmbeddingModel:
    
    def __init__(self, encoder: Encoder) -> None:
        self.stop_words = set(stopwords.words('english'))
        self.__encoder = encoder
        self.model_name = encoder.model_name
        self.__memo = dict()
        
    def __preprocess_text(self, text):
        text = text.replace('{html}', "")
        stripTags = re.compile('<.*?>')
        text = re.sub(stripTags,'',text)
        text = re.sub('http\S+','',text)
        
        words = nltk.word_tokenize(text)
        words = [word.lower() for word in words if word.isalpha() and word.lower() not in self.stop_words]
        return ' '.join(words)
    
    def encode(self, value) -> np.array:  
        if type(value) != str:
            value = str(value)

        v = self.__preprocess_text(value)
        if v not in self.__memo:
            self.__memo[v] = self.__encoder.encode(v)

        return self.__memo[v]
    
    def similarity(self, source, target):
        score = cosine_similarity([source], [target])
        return score
    
def embedding_model_provider(name: EmbModelName, variant) -> Encoder:
    """
    Factory method for creating embedding models. 

    Args:
        name (EmbModelName): the name of the embedding model, one of
            'mistral', 'bert', 'openai', 'sentence_transformer'
        variant (str, optional): an optional variant of the model. Defaults to None.

    Returns:
        Encoder: an instance of the requested embedding model
    """
    enc = None
    
    if name == EmbModelName.Mistral:
        enc = MistralEncoder(variant)
    elif name == EmbModelName.Bert:
        enc = BertEncoder(variant)
    elif name == EmbModelName.OpenAI:
        enc = OpenAIEncoder(variant)
    elif name == EmbModelName.SentenceTransformer:
        enc = SentenceTransformenEncoder(variant)

    if enc is not None:
        return EmbeddingModel(enc)
    
    raise ValueError(f"Invalid embedding model name: {name}")
    
if __name__ == '__main__':
    a = 'hello'
    b = 'greetings'
    
    emb_mod = embedding_model_provider('openai', 'text-embedding-3-small')
    val_a = emb_mod.encode(a)
    val_b = emb_mod.encode(b)
 
    print(emb_mod.similarity(val_a, val_b))