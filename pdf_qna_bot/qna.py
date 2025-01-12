from transformers import pipeline

# Model and tokenizer for question-answering
model_name = "deepset/roberta-base-squad2"

# Load the model and tokenizer using transformers pipeline
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

# Function for Question-Answering
def nlp_qna(context, question):
    QA_input = {
        'question': question,
        'context': context
    }
    res = nlp(QA_input)
    
    # Return the answer text
    return res.get('answer', "Sorry, I couldn't find an answer.")
