import os
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.readers.file import FlatReader
from llama_index.core.indices.service_context import ServiceContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pathlib import Path

api_key = os.getenv("AzureAIKey")
azure_endpoint = "https://secondapi.openai.azure.com/"
api_version="2024-02-15-preview"

llm = AzureOpenAI(
    engine="test-gpt-4",
    model="gpt-4-32k",
    temperature=0.0,
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)

embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="embedding-test",
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)

Settings.llm = llm
Settings.embed_model = embed_model
# llm_predictor = LLMPredictor(llm=llm)
# ervice_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
documents = FlatReader().load_data(Path("./data/paul_graham_essay.txt"))
# embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
# service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)
index = VectorStoreIndex.from_documents(documents)

query = "What did the author do growing up?"
query_engine = index.as_query_engine()
response = query_engine.query(query)

print(response.get_formatted_sources())
print("query was:", query)
print("answer was:", response)




