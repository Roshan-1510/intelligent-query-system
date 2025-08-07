import modal
from modal import Mount
from main import app as fastapi_app  # Assumes main.py is in the same directory
import os

print("DIR CONTENTS:", os.listdir())

app = modal.App(name="intelligent-query-system")

# ✅ Mount the current directory into the container
volume = Mount.from_local_dir(".", remote_path="/app")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install_from_requirements("requirements.txt")
)

@app.function(image=image, mounts=[volume])
@modal.asgi_app()
def fastapi_modal_app():
    return fastapi_app
