import argparse
import logging
import sys
import re
import os
import argparse

import requests
from pathlib import Path
from urllib.parse import urlparse

from llama_index.core import StorageContext
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.readers.file import FlatReader
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

from llama_index.core.prompts import ChatMessage, MessageRole, ChatPromptTemplate
from llama_index.core.postprocessor import SentenceTransformerRerank, MetadataReplacementPostProcessor
from llama_index.core.indices.query.schema import QueryBundle
from llama_index.core.schema import BaseNode, ImageNode, MetadataMode

from custom.my_sentence_window import MySentenceWindowNodeParser

from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import Settings


QA_PROMPT_TMPL_STR = (
    "Please read the provided content carefully and then give the anwser based on the provided content. The content is given in format 'url: url_address content'. If the given content containers the answer, please give the answer firstly, and then paste the url_address to record the answer source. If the provided content doesn't contains the answer of the question, please reply i don't know. Answer format as below:"
    "--------------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Question: {query_str}\n"
    "Answer: "

)

QA_SYSTEM_PROMPT = "You are a precise engineer. you will read the provided content carefully and then give the precise answer. you will also give the url_address of the answer to prove your answer is correct. You will explain if the provided content contains answer of the question"

REFINE_PROMPT_TMPL_STR = ( 
    "you are an answer correction engineer, and you will strictly adhere to the following methods of work"
    "1. only when the original answer is i don't know, then you will overwrite the old answer, otherwise you will append your answer to the original answer"
    "2. when you do the correction, you like to give the url_address to give the source of the answer"
    "3. if you are confused with new knowledge, use the original answer as your answer"
    "new knowledge: {context_msg}\n"
    "question: {query_str}\n"
    "original answer: {existing_answer}\n"
    "new answer: "
)

class Executor:
    def __init__(self, model):
        pass

    def build_index(self, path, overwrite):
        pass

    def build_query_engine(self):
        pass
     
    def delete_file(self, path):
        pass
    
    def query(self, question):
        pass
 

class MilvusExecutor(Executor):
    def __init__(self, config):
        self.index = None
        self.query_engine = None
        self.config = config
        self.api_key = os.getenv("AzureAIKey")
        self.node_parser = MySentenceWindowNodeParser.from_defaults(
            # it should be better to use re.split other than re.findall, but current expression should can work, so that no modify on it
            sentence_splitter=lambda text: re.findall('[^，；。？！,;\.\?!$\n]+?(?:[，；。？！,;\.\?!$\n]|%2C)', re.sub('[ \t]{2,}', " ", text)),
            window_size=config.milvus.window_size,
            window_metadata_key="window",
            original_text_metadata_key="original_text",)

        embed_model = AzureOpenAIEmbedding(
            model="text-embedding-ada-002",
            deployment_name="embedding-test",
            api_key=self.api_key,
            azure_endpoint=self.config.azure.azure_endpoint,
            api_version=self.config.azure.api_version,
        )
        llm = AzureOpenAI(
            engine="test-gpt-4",
            model="gpt-4-32k",
            temperature=0.0,
            api_key=self.api_key,
            azure_endpoint=self.config.azure.azure_endpoint,
            api_version=self.config.azure.api_version,
         )

        Settings.llm = llm
        Settings.embed_model = embed_model
        rerank_k = config.milvus.rerank_topk
        self.rerank_postprocessor = SentenceTransformerRerank(
            model=config.rerank.name, top_n=rerank_k)
        self._milvus_client = None
        self._debug = False
        
    def set_debug(self, mode):
        self._debug = mode

    def build_index(self, path, overwrite):
        config = self.config
        vector_store = MilvusVectorStore(
            uri = f"http://{config.milvus.host}:{config.milvus.port}",
            collection_name = config.milvus.collection_name,
            dim=config.embedding.dim,
            overwrite=overwrite)
        self._milvus_client = vector_store._milvusclient
         
        if path.endswith('.txt'):
            if os.path.exists(path) is False:
                print(f'(rag) 没有找到文件{path}')
                return
            else:
                documents = FlatReader().load_data(Path(path))
                documents[0].metadata['file_name'] = documents[0].metadata['filename'] 
        elif os.path.isfile(path):           
            print('(rag) 目前仅支持txt文件')
        elif os.path.isdir(path):
            if os.path.exists(path) is False:
                print(f'(rag) 没有找到目录{path}')
                return
            else:
                documents = SimpleDirectoryReader(path).load_data()
        else:
            return

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        nodes = self.node_parser.get_nodes_from_documents(documents)
        self.index = VectorStoreIndex(nodes, storage_context=storage_context, show_progress=True)

    def _get_index(self):
        config = self.config
        vector_store = MilvusVectorStore(
            uri = f"http://{config.milvus.host}:{config.milvus.port}",
            collection_name = config.milvus.collection_name,
            dim=config.embedding.dim)
        self.index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        self._milvus_client = vector_store._milvusclient

    def build_query_engine(self):
        config = self.config
        if self.index is None:
            self._get_index()
        self.query_engine = self.index.as_query_engine(node_postprocessors=[
            self.rerank_postprocessor,
            MetadataReplacementPostProcessor(target_metadata_key="window")
        ])
        self.query_engine._retriever.similarity_top_k=config.milvus.retrieve_topk

        message_templates = [
            ChatMessage(content=QA_SYSTEM_PROMPT, role=MessageRole.SYSTEM),
            ChatMessage(
                content=QA_PROMPT_TMPL_STR,
                role=MessageRole.USER,
            ),
        ]
        chat_template = ChatPromptTemplate(message_templates=message_templates)
        self.query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": chat_template}
        )
        self.query_engine._response_synthesizer._refine_template.conditionals[0][1].message_templates[0].content = REFINE_PROMPT_TMPL_STR

    def delete_file(self, path):
        config = self.config
        if self._milvus_client is None:
            self._get_index()
        num_entities_prev = self._milvus_client.query(collection_name=config.milvus.collection_name,filter="",output_fields=["count(*)"])[0]["count(*)"]
        res = self._milvus_client.delete(collection_name=config.milvus.collection_name, filter=f"file_name=='{path}'")
        num_entities = self._milvus_client.query(collection_name=config.milvus.collection_name,filter="",output_fields=["count(*)"])[0]["count(*)"]
        print(f'(rag) 现有{num_entities}条，删除{num_entities_prev - num_entities}条数据')
    
    def query(self, question):
        if self.index is None:
            self._get_index()
        if question.endswith('?') or question.endswith('？'):
            question = question[:-1]
        if self._debug is True:
            contexts = self.query_engine.retrieve(QueryBundle(question))
            for i, context in enumerate(contexts): 
                print(f'{question}', i)
                content = context.node.get_content(metadata_mode=MetadataMode.LLM)
                print(content)
            print('-------------------------------------------------------参考资料---------------------------------------------------------')
        response = self.query_engine.query(question)
        return response

