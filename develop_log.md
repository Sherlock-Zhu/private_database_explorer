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

### 03/13

too many changes between llamaindex 0.9 and 0.10, it's very unfriendly since i need to restruct a lot of codes....but cannot find official document for 0.9, what a pity!
besides, azure openAI also is difficult to be used. hope i have gpt4 tokens for test...

work is harder then expected, just have basic understand how to play with azure openAI with llamaindex today. need more effort tomorrow.

### 03/14

hmmmm, it seems his rag for azure openAI can work now, but memory exhausted, need to configure a better sever tomorrow...

### 03/15

after switch a server, it currently works well.
now need to migrate from his_rag to wiki_rag

### 03/16

works for llama index part done, it can work as expected now, need further check about the overall design

### 03/17

remove unnecessary doc and content from hisrag.
make a draft design at this moment, start clawler part's work

### 03/19

met an issue that when use milvus, it reported "code=1100, message=the length (76464) of dynamic field exceeds max length (65536): expected=valid length dynamic field, actual=length exceeds max length: invalid parameter"
guess it's because the node is too long, trying to find a better way to split the sentence.

### 03/20

re-learning regular expression...

### 03/22

job done, but seems not as good as i expected, will further check llamaindex usage.

### 03/24

Stopped here for a while, will back next week
