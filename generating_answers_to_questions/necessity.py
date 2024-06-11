import os
import sys
sys.path.append('/Users/anastasia/Desktop/ML/Диплом')
from my_library.smart_html_splits import *
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma
from langchain_community.llms import GigaChat
from langchain_core.runnables import RunnablePassthrough
from langchain.docstore.document import Document
from langchain.schema.runnable import RunnableLambda
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain.retrievers import  ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank

# LangSmith
# os.environ["LANGCHAIN_PROJECT"] = "FINAL_3"
os.environ["LANGCHAIN_TRACING_V2"] = 'true'
os.environ["LANGCHAIN_API_KEY"] = "YOUR"

# Cohere 
import cohere
os.environ["COHERE_API_KEY"] = "YOUR"
co = cohere.Client(os.environ["COHERE_API_KEY"])

# OpenAI proxy
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
os.environ["OPENAI_API_KEY"] = "YOUR"
os.environ["OPENAI_BASE_URL"] = 'https://api.proxyapi.ru/openai/v1'

# GigaChat
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
client_id = 'YOUR'
client_secret = 'YOUR'
authorization_data = 'YOUR'
os.environ["GIGACHAT_CREDENTIALS"] = authorization_data



# получаем только уникальные документы из всего списка
def get_unique_documents(documents):
    unique_documents = []
    seen_contents = set()

    for doc in documents:
        content = doc.page_content
        if content not in seen_contents:
            unique_documents.append(doc)
            seen_contents.add(content)

    return unique_documents

# по списку документов получаем определенный с page_content=target_page_content
def get_document_by_content(documents, target_page_content):
    for doc in documents:
        if doc.page_content == target_page_content:
            return doc

# Определяем функцию rerank_doc
def rerank_doc(query: str, top_n: int, documents):
    unique_docs = get_unique_documents(documents)
    
    # Rerank documents
    rerank_results = co.rerank(
        query=query, 
        documents=[doc.page_content for doc in unique_docs], 
        top_n=top_n, 
        model="rerank-multilingual-v3.0",
        return_documents=True
    )
    
    reranked_docs = []
    
    for info in rerank_results.results:
        doc = get_document_by_content(unique_docs, info.document.text)
        doc.metadata['relevance_score'] = info.relevance_score
        reranked_docs.append(doc)
        
    return reranked_docs