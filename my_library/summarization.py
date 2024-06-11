import re
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter
import ssl
import nltk

# Деактивация проверки сертификатов в NLTK 
ssl._create_default_https_context = ssl._create_unverified_context
nltk.download("punkt")  # Загрузка ресурса "punkt" для токенизации

def summarize_text(text):
    """
    Создает краткую суммаризацию текста на основе наиболее часто встречающихся слов.
    
    Аргументы:
    - text (str): Текст для суммаризации.
    
    Возвращает:
    - str: Краткая суммаризация текста.
    """
    # Загрузка списка стоп-слов для русского языка
    stop_words = set(stopwords.words("russian"))

    # Регулярное выражение для токенизации предложений и фильтрации слов
    sentence_splitter = re.compile(r'(?<!\d)\.(?! \d)|\.(?![a-z])')
    word_filter = re.compile(r'[^\W\d]+')

    # Токенизация текста на предложения
    sentences = sentence_splitter.split(text)

    # Токенизация предложений на слова и удаление стоп-слов
    words = [word for sentence in sentences for word in word_tokenize(sentence) if word_filter.match(word) and word.lower() not in stop_words]

    # Подсчет частоты слов
    word_freq = Counter(words)

    # Выбор наиболее часто встречающихся слов
    top_words = word_freq.most_common(3)

    # Формирование краткой суммаризации на основе этих слов
    summary = ' '.join([word[0] for word in top_words])

    return summary

# Пример использования:
if __name__ == "__main__":
    text = """
    Перечень документов и сведений, предоставляемых Клиентом (представителем Клиента) для присоединения к условиям Универсального договора, а также в целях обслуживания в рамках Универсального договора (далее — Перечень)
    """