import logging
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

# Setup logger for this module
# Configure logging level. You might want to do this globally in your app's entry point.
# If not configured elsewhere, basicConfig will set it up.
logger = logging.getLogger(__name__)
if not logger.hasHandlers(): # Avoid adding multiple handlers if already configured
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define the Hugging Face model identifier
model_identifier = "ashutoshj01/bert-finetuned-squad"

# Global variable for the pipeline, initialized to None
question_answerer = None

def load_model_and_pipeline():
    """Loads the model, tokenizer, and creates the Q&A pipeline."""
    global question_answerer
    try:
        logger.info(f"Attempting to load model and tokenizer from Hugging Face Hub: {model_identifier}")
        model = AutoModelForQuestionAnswering.from_pretrained(model_identifier)
        tokenizer = AutoTokenizer.from_pretrained(model_identifier)
        question_answerer = pipeline("question-answering", model=model, tokenizer=tokenizer)
        logger.info(f"Successfully loaded model and tokenizer for '{model_identifier}'. Q&A pipeline is ready.")
    except Exception as e:
        logger.error(f"CRITICAL: Error loading model/tokenizer for '{model_identifier}': {e}", exc_info=True)
        question_answerer = None # Ensure pipeline is None if loading fails

# Attempt to load the model and pipeline when this module is first imported.
# This will happen when your FastAPI application starts up and imports this module.
load_model_and_pipeline()

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
        logger.warning("Q&A pipeline is not loaded or failed to load. Returning placeholder response.")
        return "Model is not loaded, so this is a placeholder response."

    logger.info(f"Processing question with loaded model. Question: '{question[:70]}...' Context: '{context[:70]}...'")
    # The pipeline function handles input validation internally
    # It returns a dictionary like {'score': 0.99, 'start': 10, 'end': 25, 'answer': 'the answer'}
    try:
        result = question_answerer(question=question, context=context)
        answer = result.get('answer', '')
        logger.info(f"Model returned answer: '{answer[:70]}...' (Score: {result.get('score', 'N/A')})")
        return answer
    except Exception as e:
        logger.error(f"Error during Q&A pipeline execution: {e}", exc_info=True)
        return f"Error processing question: {e}"