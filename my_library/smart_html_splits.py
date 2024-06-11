# библиотеки
from langchain_text_splitters import HTMLHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
import json
import os

# Умная разбивка документов -> html - > по разделам -> по чанкам с метаданными вввиде названий разделов
def split_documents_html(chunk_size, chunk_overlap, flag=True):
    file_path = "../generating_answers_to_questions/docs_html.json"
    # Загрузка данных
    with open(file_path, "r") as file:
        all_documents = json.load(file)
    
    # Модификация документов
    modified_all_documents = [s.replace('<h4>', '<p>').replace('</h4>', '</p>')[14:] for s in all_documents]

    # Заголовки для разделения
    headers_to_split_on = [
        ("h1", "Header 1"),
        ("h2", "Header 2"),
    ]

    # Создание сплиттеров
    html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    splits = []
    
    # Разделение документов
    for elem in modified_all_documents:
        html_header_splits = html_splitter.split_text(elem)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        if flag:
            splits += text_splitter.split_documents(html_header_splits)
        else:
            splits.append(text_splitter.split_documents(html_header_splits))
    
    return splits

# умная разбивка по смысловым кускам в +- предлеах 100-200 токенов
def split_documents_my_html():
    
    file_path = "../generating_answers_to_questions/smart_chunks_100.json"
    with open(file_path, "r") as file:
        all_chunks = json.load(file)

    # Создаем массив объектов LangChainDocument
    splits = []
    for i, chunk in enumerate(all_chunks):
        document = Document(page_content=chunk, metadata={"source": "../data/Пользовательское соглашение Тинькофф", 'page': i})
        splits.append(document)
    return splits
    
    
def split_documents_standart(chunk_size, chunk_overlap,flag=True):
    
    folder_path = "../data/Пользовательское соглашение Тинькофф"
    splits = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(folder_path, filename)).load()
            if flag:
                splits += text_splitter.split_documents(loader)
            else:
                splits.append(text_splitter.split_documents(loader))
        
    return splits

    
# максимальная длина чанка в токенах
def find_max_chunk_length(splits):
    max_length = 0
    for elem in splits:
        chunk_length = len(elem.page_content.split())
        if chunk_length > max_length:
            max_length = chunk_length
    return max_length

