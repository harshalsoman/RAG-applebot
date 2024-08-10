# import os
# import faiss
# from sentence_transformers import SentenceTransformer
# from llama_cpp import Llama
# from data_processing import save_embeddings, load_embeddings
#
# MODEL_PATH = "bartowski/Llama-3-Instruct-8B-SPPO-Iter3-GGUF"  # Update with your model path
# CHUNKS_FILE = "saved_chunks.pkl"
# EMBEDDINGS_FILE = "embeddings.pkl"
#
#
# def load_llama_model():
#     from huggingface_hub import hf_hub_download
#
#     # Replace 'TheBloke/TinyLlama-1.1B-Chat-v0.3-GGUF' with your model repository
#     # Replace 'tinyllama-1.1b-chat-v0.3.Q4_K_M.gguf' with the specific GGUF file you want to download
#     model_path = hf_hub_download(repo_id='bartowski/Meta-Llama-3-8B-Instruct-GGUF',
#                                  filename='Meta-Llama-3-8B-Instruct-IQ1_M.gguf')
#
#     print(f"Model downloaded to: {model_path}")
#     try:
#         model = Llama(model_path=model_path)
#         return model, None
#     except Exception as e:
#         print(f"Error loading model: {e}")
#         return None, None
#
#
# def implement_rag(all_chunks, embeddings_file=EMBEDDINGS_FILE):
#     # Initialize embedding model
#     embed_model = SentenceTransformer('all-MiniLM-L6-v2')
#
#     # Check if embeddings file exists
#     if os.path.exists(embeddings_file):
#         embeddings = load_embeddings(embeddings_file)
#     else:
#         # Create vector database
#         embeddings = embed_model.encode(all_chunks)
#         save_embeddings(embeddings, embeddings_file)
#
#     dimension = embeddings.shape[1]
#
#     faiss.normalize_L2(embeddings)
#
#     index = faiss.IndexFlatIP(dimension)
#     index.add(embeddings)
#
#     return embed_model, index, all_chunks
#
#
# def retrieve(query, embed_model, index, chunks, k=5):
#     query_vector = embed_model.encode([query])
#     faiss.normalize_L2(query_vector)
#     _, indices = index.search(query_vector, k)
#     return [chunks[i] for i in indices[0]]
#
#
# def generate_response(query, context,tokenizer, model):
#     prompt = f"Query: {query}\nContext: {context[:500]}\nAnswer:"
#     response = model(prompt, max_tokens=50, stop=["\n"])
#
#     return response['choices'][0]['text'].strip()