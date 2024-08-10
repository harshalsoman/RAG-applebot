import streamlit as st

from google_t5_model import load_google_t5_model, implement_rag as implement_rag_t5, retrieve as retrieve_t5, \
    generate_response as generate_response_t5
from llama import load_llama_model, generate_response as generate_response_llama
from data_processing import download_sec_filings, preprocess_filing, save_chunks,load_chunks
import os
CHUNKS_FILE = "saved_chunks.pkl"

def run_chat():
    # Streamlit app

    st.write("Currently only 1 model is supported. Adding more soon!")
    # Model selection
    model_choice = st.selectbox("Choose a model:", ["Google T5","LLama3"])

    @st.cache_resource
    def load_model_and_rag(model_choice):
        if model_choice == "Google T5":
            st.session_state.chat_history = []
            model, tokenizer = load_google_t5_model()
            implement_rag = implement_rag_t5
            retrieve = retrieve_t5
            generate_response = generate_response_t5
        else:
            st.session_state.chat_history = []
            model,tokenizer = load_llama_model()
            implement_rag = implement_rag_t5
            retrieve = retrieve_t5
            generate_response = generate_response_llama



        # Load or download and preprocess filings
        if os.path.exists(CHUNKS_FILE):
            all_chunks = load_chunks(CHUNKS_FILE)
        else:
            filings = download_sec_filings()
            all_chunks = []
            for filing in filings:
                all_chunks.extend(preprocess_filing(filing))
            save_chunks(all_chunks, CHUNKS_FILE)

        print(f'Total chunks created: {len(all_chunks)}')

        # Implement RAG system
        embed_model, index, chunks = implement_rag(all_chunks)

        return model, tokenizer, embed_model, index, chunks, generate_response, retrieve

    model, tokenizer, embed_model, index, chunks, generate_response, retrieve = load_model_and_rag(model_choice)

    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Callback function to handle user input
    def handle_user_input():
        user_input = st.session_state.user_input
        retrieved_chunks = retrieve(user_input, embed_model, index, chunks)
        context = ' '.join(retrieved_chunks)

        response = generate_response(user_input, context, tokenizer, model)

        # Update chat history
        st.session_state.chat_history.append({"query": user_input, "response": response})

        # Clear input box
        st.session_state.user_input = ""

    # User input
    st.text_input("Ask a financial question about Apple:", key="user_input", on_change=handle_user_input)

    for chat in reversed(st.session_state.chat_history):
        st.write(f"**You:** {chat['query']}")
        st.write(f"**Bot:** {chat['response']}")
        st.write("---")
