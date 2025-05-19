from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

# Define the path where the model weights will be mounted
# This path corresponds to the volume mount in your Kubernetes deployment
model_path = "/mnt/model"

# Load model and tokenizer at module startup.
# This happens only once when the qna_engine module is first imported by your FastAPI app.
# The init container in Kubernetes is responsible for ensuring the model files are at model_path
try:
    model = AutoModelForQuestionAnswering.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    # Create the question answering pipeline using the loaded model and tokenizer
    question_answerer = pipeline("question-answering", model=model, tokenizer=tokenizer)
    print(f"Successfully loaded model from {model_path}")
except Exception as e:
    print(f"Error loading model from {model_path}: {e}")
    # Depending on your error handling strategy, you might want to
    # re-raise the exception or handle it gracefully.
    # For now, we'll print the error and the pipeline might fail later.
    question_answerer = None # Ensure pipeline is None if loading fails

def get_answer(context: str, question: str, model_version: str = None) -> str:
    """
    Uses the pre-loaded question answering pipeline to find an answer
    within the given context for the provided question.

    Args:
        context: The text context to search within.
        question: The question to answer.
        model_version: This parameter is included for API compatibility
                       but is not used internally as the model is pre-loaded.

    Returns:
        The extracted answer string, or an empty string/error message
        if the pipeline fails or no answer is found.
    """
    if question_answerer is None:
        print("model is not loaded, so this is a placeholder response")
        return "model is not loaded, so this is a placeholder response"

    # The pipeline function handles input validation internally
    # It returns a dictionary like {'score': 0.99, 'start': 10, 'end': 25, 'answer': 'the answer'}
    try:
        result = question_answerer(question=question, context=context)
        return result.get('answer', '') # Return the answer or an empty string if 'answer' key is missing
    except Exception as e:
        print(f"Error during Q&A pipeline execution: {e}")
        return f"Error processing question: {e}"