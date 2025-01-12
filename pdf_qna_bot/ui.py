import streamlit as st
import requests
from ocr import extract_text_from_pdf  # Import function from ocr.py

# Function to get the answer from the FastAPI backend
def get_answer(context, question):
    # Define the FastAPI endpoint URL (assuming FastAPI is running locally)
    FASTAPI_URL = "http://localhost:8005"
    
    # Make a POST request to the FastAPI endpoint
    response = requests.post(f"{FASTAPI_URL}/qna/", json={"context": context, "question": question})

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data.get("answer", "Sorry, I couldn't find an answer.")
    else:
        return "Error: Failed to get answer"

# Streamlit UI
def main():
    st.title("PDF Question Answering System")
    
    # Step 1: Upload PDF file
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    
    if uploaded_file:
        # Step 2: Extract text from PDF using OCR
        with st.spinner("Processing PDF..."):
            context = extract_text_from_pdf(uploaded_file)
        
        if context:
            st.subheader("Extracted Text")
            st.write(context)  # Show extracted text
            
            # Step 3: Input Question
            question = st.text_input("Enter your question")
            
            if question:
                # Step 4: Get Answer from Q&A Bot
                with st.spinner("Getting answer..."):
                    answer = get_answer(context, question)
                    st.subheader("Answer")
                    st.write(answer)  # Show the answer

if __name__ == "__main__":
    main()
