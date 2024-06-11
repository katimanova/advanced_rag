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