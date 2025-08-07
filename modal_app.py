from fastapi import FastAPI
import modal

from main import app as fastapi_app  # Import your FastAPI app from main.py

app = modal.App(name="intelligent-query-system")

image = modal.Image.debian_slim(python_version="3.10").pip_install_from_requirements("requirements.txt")

@app.function(image=image, min_containers=1)
@modal.asgi_app()
def fastapi_modal_app():
    return fastapi_app
