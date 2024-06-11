from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

class BaseRag():
    def __init__(self, llm, embeddings_model, vector_store=FAISS, prompt=None):
        self.llm = llm
        self.embeddings_model = embeddings_model
        self.vector_store = vector_store
        self.prompt = prompt
    
    def chain(self, documents):
        # Создаем векторное хранилище из массива документов
        self.db = self.vector_store.from_documents(documents=documents, embedding=self.embeddings_model)
        
        # Устанавливаем ретриевер для поиска контекста
        self.retriever = self.db.as_retriever(
            search_type="mmr",
            search_kwargs={'k': 1, 'lambda_mult': 0.25}
        )
        
        # Определяем цепочку обработки данных
        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def __call__(self, questions):
        # Выполняем цепочку обработки данных для вопросов
        return self.rag_chain.invoke(questions)
    