from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os


class BaseRag():
    def __init__(self, llm, embeddings_model, text_splitter=None, prompt=None):
        
        self.llm = llm
        self.text_splitter = text_splitter
        self.embeddings_model = embeddings_model
        self.vector_strore = FAISS
        self.prompt = prompt
    
    def chain(self):

        self.db = self.vector_strore.from_documents(documents=self.splits_docs,
                                                    embedding=self.embeddings_model)
        # self.retriever = self.db.as_retriever()
        self.retriever = self.db.as_retriever(
                                search_type="mmr",
                                search_kwargs={'k': 1, 'lambda_mult': 0.25}
                            )
        
        self.rag_chain = (
            {"context": self.retriever | self.format_chunks, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def chanking_data(self, docs):

        self.splits_docs = self.text_splitter.split_documents(docs)
        
        return self.splits_docs
    
    
    def __call__(self, questions):
        return self.rag_chain.invoke(questions)
    
    @staticmethod
    def format_chunks(docs):
        return "\n\n".join(doc.page_content for doc in docs)
        