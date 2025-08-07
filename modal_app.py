import modal
from main import app as fastapi_app  # Assumes main.py is in the same directory

app = modal.App(name="intelligent-query-system")

image = modal.Image.debian_slim(python_version="3.10").pip_install_from_requirements("requirements.txt")

@app.function(image=image)
@modal.asgi_app()
def fastapi_modal_app():
    return fastapi_app
