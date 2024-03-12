# Dev Log

## start date

2024-03-11

## records

### first of all

This repo start from 2024/03/11, hopefully I can get some draft result on 04/11. this log will record all the questions and the changes of my mantality.
Note：Don't give up! Come on!

### 03/11

project start, come on!

#### initial Plan

Firstly will try below model:
LLM Model: Azure OPENAI
Vector database: milvus
data source: local txt file(use scrapy to download from internet)

later may migrate to below model:
LLM Model: local LLM model like LLama2 7B or chatGLM 6B to save cost
Vector database: mongoDB which support vector storage
data source: database like mongoDB or SQL(scrapy download from internet and store to database directly, don't storage the data locally)
             (rare possible) if there is such connector in the future and network conditional is good enough, use LLM connector to download from internet directly. no need to pre store any data.

PS: at this moment, LLama_index is the main process for "RAG" part since it's more friendly for a rookie like me, later may swithc to langchain, just a note here

### 03/12

today roughly went through all the codes of history_rag, but still some query engine build logic are not very clear, will leave it in the future verification part to double research.
tomorrow will try to extract the useful code and make it adapt to Azure OpenAI.
