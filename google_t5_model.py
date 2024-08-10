import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import faiss
from data_processing import save_embeddings, load_embeddings
import os

def load_google_t5_model():
    model_name = 'google/flan-t5-base'

    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    return model, tokenizer


def implement_rag(all_chunks, embeddings_file='embeddings.pkl'):
    # Initialize embedding model
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Check if embeddings file exists
    if os.path.exists(embeddings_file):
        embeddings = load_embeddings(embeddings_file)
    else:
        # Create vector database
        embeddings = embed_model.encode(all_chunks)
        save_embeddings(embeddings, embeddings_file)

    dimension = embeddings.shape[1]

    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    return embed_model, index, all_chunks


def retrieve(query, embed_model, index, chunks, k=5):
    query_vector = embed_model.encode([query])
    faiss.normalize_L2(query_vector)
    _, indices = index.search(query_vector, k)
    return [chunks[i] for i in indices[0]]


def generate_response(query, context, tokenizer, model):
    prompt = f"Query: {query}\nContext: {context}\nAnswer:"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,  # Generate up to 200 new tokens
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            top_k=50,
            top_p=0.95,

        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return response.split("Answer:")[-1].strip()
