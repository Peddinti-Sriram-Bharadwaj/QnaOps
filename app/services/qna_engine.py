# Import necessary components from transformers
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

# Define the path or name for the HuggingFace model
model_path = "/mnt/model"  # or a HuggingFace model name

# Load model and tokenizer at module startup for efficiency
model = AutoModelForQuestionAnswering.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Create the question answering pipeline
question_answerer = pipeline("question-answering", model=model, tokenizer=tokenizer)

def get_answer(context: str, question: str, model_version: str) -> str:
    """
    Uses the pre-loaded question answering pipeline to find an answer
    within the given context for the provided question.
    """
    # The pipeline function handles input validation internally
    result = question_answerer(question=question, context=context)
    return result['answer']