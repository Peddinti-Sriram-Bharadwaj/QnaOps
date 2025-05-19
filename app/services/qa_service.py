# app/services/qa_service.py
from transformers import pipeline
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Model Loading ---
# The model is expected to be pre-downloaded by an initContainer to MODEL_DIR.
# This path corresponds to the volumeMount in your Kubernetes deployment for the main app container.
MODEL_DIR = "/mnt/model" # This should match the mountPath for 'model-storage' volume

# IMPORTANT: The model loaded here MUST be the one downloaded by your initContainer.
# The initContainer in k8s-fastapi.yaml is currently set to download
# "distilbert-base-uncased-distilled-squad" via the HF_MODEL_NAME environment variable.
# If you want to use "ashutoshj01/bert-finetuned-squad" (from your script),
# you MUST change HF_MODEL_NAME in k8s-fastapi.yaml.
# See the suggested modifications to k8s-fastapi.yaml later.

question_answerer_pipeline = None

try:
    logger.info(f"Attempting to load question-answering model from: {MODEL_DIR}")
    if os.path.exists(MODEL_DIR) and os.listdir(MODEL_DIR):
        # When loading from a local directory, provide the directory path to both model and tokenizer
        question_answerer_pipeline = pipeline("question-answering", model=MODEL_DIR, tokenizer=MODEL_DIR)
        logger.info(f"Successfully loaded model from {MODEL_DIR}")
    else:
        logger.error(f"Model directory {MODEL_DIR} is empty or does not exist. "
                     "Ensure the initContainer has downloaded the model correctly, "
                     "HF_MODEL_NAME in k8s-fastapi.yaml matches the desired model, "
                     "and the volumeMount for the main container is correctly configured.")
except Exception as e:
    logger.error(f"Error loading model from {MODEL_DIR}: {e}", exc_info=True)
    # In a production scenario, you might want to raise an error or have a more robust fallback.
    # For now, the pipeline remains None, and endpoints will indicate model unavailability.

def get_answer(question: str, context: str) -> dict:
    if not question_answerer_pipeline:
        logger.error("Question answering pipeline is not initialized.")
        return {"error": "Model not loaded", "answer": None, "score": 0.0, "start": None, "end": None}

    logger.info(f"Processing question: '{question}' with context.")
    try:
        result = question_answerer_pipeline(question=question, context=context)
        return result
    except Exception as e:
        logger.error(f"Error during question answering: {e}", exc_info=True)
        return {"error": "Error processing request", "answer": None, "score": 0.0, "start": None, "end": None}

