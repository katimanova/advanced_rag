# Импорт необходимых библиотек
import sys
sys.path.append('/Users/anastasia/Desktop/ML/Диплом')
import pdfplumber
from bs4 import BeautifulSoup
from my_library.summarization import *
import re

# Функция для извлечения информации о тексте из PDF-файла
def extract_text_info(pdf_path):
    """
    Извлекает информацию о тексте из PDF-файла.
    
    Аргументы:
    - pdf_path (str): Путь к PDF-файлу.
    
    Возвращает:
    - list: Список словарей, содержащих информацию о тексте.
    """
    text_info = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            current_word = ""
            current_word_bold = False
            prev_font_size = None  
            for obj in page.chars:
                if obj['text'].strip():
                    current_font_size = round(obj['size']) 
                    # Проверяем, является ли текущая буква жирной
                    current_bold = 'Bold' in obj['fontname']
                    if current_font_size != prev_font_size or current_bold != current_word_bold:
                        if current_word:
                            text_info.append({
                                'text': current_word,
                                'font_size': prev_font_size,
                                'font_name': obj['fontname'],
                                'font_bold': current_word_bold,
                                'font_italic': 'Italic' in obj['fontname']
                            })
                            current_word = ""
                    current_word += obj['text']
                    current_word_bold = current_bold
                    prev_font_size = current_font_size
                else:
                    if current_word:
                        text_info.append({
                            'text': current_word,
                            'font_size': prev_font_size,
                            'font_name': obj['fontname'],
                            'font_bold': current_word_bold,
                            'font_italic': 'Italic' in obj['fontname']
                        })
                        current_word = ""  
            if current_word:
                text_info.append({
                    'text': current_word,
                    'font_size': prev_font_size,
                    'font_name': obj['fontname'],
                    'font_bold': current_word_bold,
                    'font_italic': 'Italic' in obj['fontname']
                })
    return text_info


# Функция для обработки текста и применения форматирования
def process_text(text_info):
    """
    Обрабатывает информацию о тексте и применяет форматирование.
    
    Аргументы:
    - text_info (list): Список словарей, содержащих информацию о тексте.
    
    Возвращает:
    - str: Обработанный текст с форматированием.
    """
    new_text = ""
    prev_format = ""
    for word_info in text_info:
        word_text = word_info['text']
        font_size = word_info['font_size']
        font_bold = word_info['font_bold']
        
        # Определяем формат для текущего слова
        current_format = ""
        if font_size in [19, 20]:
            current_format += '<h1>'
        elif font_size in [11, 12]:
            current_format += '<h2>'
        elif font_size in [8, 9]:
            current_format += '<h4>'
        
        # Обработка выделения жирным шрифтом
        bold_open_tag = ""
        if font_bold:
            bold_open_tag = '<b>'
        
        # Добавляем формат и выделение к текущему слову, если они отличаются от предыдущих
        if current_format != prev_format:
            new_text += current_format + bold_open_tag + word_text + ' '
        else:
            new_text += bold_open_tag + word_text + ' '
        
        # Обновляем значение предыдущего формата
        prev_format = current_format
    
    return new_text


# Функция для правильного форматирования жирного текста 
def format_bold(text):
    """
    Форматирует жирный текст в HTML.
    
    Аргументы:
    - text (str): Текст с HTML-тегами.
    
    Возвращает:
    - str: Отформатированный текст с правильными тегами для жирного шрифта.
    """
    count_bold = 0
    result = ""
    for words in text.split():
        if '<b>' in words:
            count_bold += 1
            if count_bold > 1:
                result += words.replace("<b>", "") + " "
            else:
                result += words + " "
        elif count_bold != 0:
            result = result[:-2]
            result += "</b> " + words + " "
            count_bold = 0
        else:
            result += words + " "
    
    return result
 
# Функция для правильного форматирования блоков текста        
def process_formatted_text(text):
    """
    Обрабатывает текст с форматированием и применяет правильное блочное форматирование.
    
    Аргументы:
    - text (str): Текст с HTML-тегами.
    
    Возвращает:
    - str: Обработанный текст с правильным блочным форматированием.
    """
    flag_h1 = False
    flag_h2 = False
    flag_h4 = False

    result = ""
    current_block = None

    for word in text.split():
        if word.startswith("<h1>"):
            if current_block == "<h4>":
                result += "</h4> "
            if current_block == "<h2>":
                result += "</h2> "
            result += word
            current_block = "<h1>"
            flag_h1 = True
        elif word.startswith("<h2>"):
            if current_block == "<h4>":
                result += "</h4> "
            if current_block == "<h1>":
                result += "</h1> "
            result += word
            current_block = "<h2>"
            flag_h2 = True
        elif word.startswith("<h4>"):
            if current_block == "<h1>":
                result += "</h1>"
            if current_block == "<h2>":
                result += "</h2>"
            result += word
            current_block = "<h4>"
            flag_h4 = True
        else:
            result += " " + word

    # Закрываем последний блок, если он не был закрыт
    if current_block == "<h1>":
        result += "</h1> "
    elif current_block == "<h2>":
        result += "</h2> "
    elif current_block == "<h4>":
        result += "</h4> "
    
    return result


# Функция для разделения HTML-документа на чанки
def split_into_chunks(html_doc):
    """
    Разбивает HTML-документ на чанки на основе заголовков.
    
    Аргументы:
    - html_doc (str): HTML-документ в виде строки.
    
    Возвращает:
    - list: Список чанков
    """
    # Парсинг HTML
    soup = BeautifulSoup(html_doc, 'html.parser')

    # Инициализация массива для хранения чанков
    chunks = []
    current_chunk = []

    # Итерация по тегам в документе
    for tag in soup.find_all(['h1', 'h2', 'h4']):
        # Получаем текст тега без пробелов в начале и конце
        text = tag.get_text(strip=True)

        # Если текущий тег - h1, добавляем текущий чанк в список чанков и начинаем новый чанк
        if tag.name == 'h1':
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
        # Если текущий тег - h2 и текущий чанк не пустой, добавляем текущий чанк в список чанков и начинаем новый чанк
        elif tag.name == 'h2' and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []

        # Добавляем текст из текущего тега в текущий чанк
        current_chunk.append(text)

    # Если остался непустой чанк, добавляем его в список чанков
    if current_chunk:
        chunks.append(current_chunk)

   # Убираем информацию о страницах из каждого чанка
    pattern = r'\b\d+\s*из\s*\d+\b'
    for chunk in chunks:
        for i in range(len(chunk)):
            chunk[i] = re.sub(pattern, '', chunk[i])

    # Удаляем пустые чанки
    chunks = [chunk for chunk in chunks if chunk != ['']]
    
    # Обработать случай на три чанка
    if len(chunks[0]) == 3:
        chunks = [[chunks[0][0], chunks[0][1] + chunks[0][2]]]
        
    return chunks


# Функция для фильтрации чанков
def filter_chunks(chunks):
    """
    Фильтрует чанки.
    
    Аргументы:
    - chunks (list): Список чанков.
    
    Возвращает:
    - list: Отфильтрованный список чанков.
    """
    # Инициализация регулярного выражения для поиска выражений типа "число из число"
    pattern = r'\b\d+\s*из\s*\d+\b'

    # Функция для удаления найденных выражений из строки
    def remove_pattern(string):
        return re.sub(pattern, '', string)

    # Преобразуем чанки в строки и фильтруем их
    str_chunks = []
    for i in range(len(chunks)):
        if len(chunks[i]) == 1 and i + 1 < len(chunks) and len(chunks[i][0]) < 130:
            combined_chunk = str(chunks[i][0]) + ". " + str(chunks[i + 1][0])
            str_chunks.append(combined_chunk)
            i += 1
        else:
            str_chunk = ". ".join(map(str, chunks[i]))
            str_chunks.append(str_chunk)

    filtered_arr = [remove_pattern(string) for string in str_chunks]

    return filtered_arr


# Функция для разделения текста на предложения
def split_into_sentences(text):
    """
    Разбивает текст на предложения.
    
    Аргументы:
    - text (str): Текст для разбиения.
    
    Возвращает:
    - list: Список предложений.
    """
    # Регулярное выражение для разделения на предложения
    sentence_splitter = re.compile(r'(?<!\d)\.|\.(?!\d)')

    # sentence_splitter = re.compile(r'(?<!\d)(?<![a-zA-Z])\.|\.(?!\d)(?![a-zA-Z])|;')
    # sentence_splitter = re.compile(r'(?<!\d\.\s)(?<![а-яА-Я]\.)(?<=\.|\;)\s(?!р[у])(?![а-яА-Я]\.\d)')
    # sentence_splitter = re.compile(r'(?<!\d)[.;]|[.;](?!\d)')

    # Находим все предложения в тексте
    sentences = sentence_splitter.split(text)
    # Удаляем завершающие пробелы из каждого предложения
    sentences = [s.strip() for s in sentences]
    
    return sentences


# Функция для разбития по токенам
def merge_chunks(chunks, max_tokens):
    """
    Объединяет чанки текста в более крупные блоки, учитывая максимальное количество токенов в блоке.
    
    Аргументы:
    - chunks (list): Список чанков текста.
    - max_tokens (int): Максимальное количество токенов в объединенном блоке.
    
    Возвращает:
    - list: Список объединенных блоков текста.
    """
    merged_chunks = []
    for chunk in chunks:
        if len(chunk) == 1:
            merged_chunks.append(chunk[0])
        else:
            start_line = chunk[0]
            new_line = start_line + '. '
            end_line = chunk[1]
            if len(new_line.split() + end_line.split()) > max_tokens:
                sentences = split_into_sentences(end_line)
                arr = []
                line_mix = start_line + '. '
                for elem in sentences:
                    line_mix += ' ' + elem
                    if len(line_mix.split()) > max_tokens:
                        if (len(line_mix.split()) > 275):
                                group = group_parts(elem)
                                for e in group:
                                    arr.append(start_line + '. ' +  e)
                        else:
                            arr.append(line_mix)
                        if len(start_line.split()) >= 10:
                            line_mix = summarize_text(start_line) + '. '
                        else:
                            line_mix = start_line + '. '
                
                if line_mix != (start_line + '.  '):
                    arr.append(line_mix)
                
                merged_chunks += arr
            else:
                new_line += end_line
                merged_chunks.append(new_line)
                
    return merged_chunks

def group_parts(text):
    # Разбить строку по указанной нумерации
    parts = re.split(r'(\s*\d+\.\s*)', text)

    # Удалить пустые элементы из списка
    parts = [part.strip() for part in parts if part.strip()]

    grouped_parts = []
    temp_part = ""
    for part in parts:
        if len(part) < 5:
            temp_part += part
        else:
            if temp_part:
                grouped_parts.append(temp_part)
                temp_part = ""
            grouped_parts.append(part)
    # Добавляем последний элемент, если он есть
    if temp_part:
        grouped_parts.append(temp_part)

    return grouped_parts

