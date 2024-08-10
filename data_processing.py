import os
import re
import pickle
import nltk
from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize

nltk.download('punkt')


def download_sec_filings():
    downloader = Downloader("./sec-edgar-filings",email_address='hsoman3@uic.edu')
    downloader.get("10-K", "AAPL")


    filings = []
    for root, dirs, files in os.walk("./sec-edgar-filings"):
        for file in files:
            if file.endswith(".txt"):
                filings.append(os.path.join(root, file))

    return filings


def preprocess_filing(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Try different parsers
    parsers = ['html.parser', 'lxml', 'html5lib']
    for parser in parsers:
        try:
            soup = BeautifulSoup(content, parser)
            break
        except Exception as e:
            print(f"Parser {parser} failed: {e}")
    else:
        print(f"All parsers failed for file: {file_path}")
        return []

    for script in soup(["script", "style"]):
        script.decompose()

    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text).strip()

    sentences = sent_tokenize(text)

    chunks = []
    current_chunk = []
    current_count = 0
    for sentence in sentences:
        words = sentence.split()
        if current_count + len(words) > 200:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_count = 0
        current_chunk.append(sentence)
        current_count += len(words)

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def save_chunks(chunks, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(chunks, f)

def load_chunks(file_path):
    with open(file_path, 'rb') as f:
        chunks = pickle.load(f)
    return chunks

def save_embeddings(embeddings, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(embeddings, f)


def load_embeddings(file_path):
    with open(file_path, 'rb') as f:
        embeddings = pickle.load(f)
    return embeddings
