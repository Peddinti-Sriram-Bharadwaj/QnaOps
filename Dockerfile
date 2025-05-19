# Stage 1: Model Weights Provider
# This stage uses the Docker Hub image containing your model weights.
# We'll copy the weights from here into the final application image.
FROM ashutoshj/trained-model-image2 AS model_weights_provider
# ------------------------------------------------------------------------------------
# IMPORTANT: You MUST determine the exact path where the model files
# (e.g., pytorch_model.bin, config.json, tokenizer.json, etc.) are located
# *inside* the 'ashutoshj/trained-model-image2' image.
#
# For this example, I'm assuming the model files are in a directory named
# '/model_files_in_image'.
#
# PLEASE REPLACE '/model_files_in_image' in the COPY command in Stage 3
# with the actual path from the 'ashutoshj/trained-model-image2' image.
# You might need to inspect the 'ashutoshj/trained-model-image2' image
# (e.g., by running it and listing directories, or checking its Dockerfile if available)
# to find this path.
# ------------------------------------------------------------------------------------

# Stage 2: Python Application Base with Dependencies
FROM python:3.9-slim AS python_dependencies_base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final Application Image
FROM python:3.9-slim

WORKDIR /app

COPY --from=python_dependencies_base /app /app
COPY ./app /app/app # Copy your application code

# Copy model weights from the model_weights_provider stage to /mnt/model
COPY --from=model_weights_provider /model_files_in_image /mnt/model 

EXPOSE 8000

# Assuming your FastAPI main application instance is in app/main.py and named 'app'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]