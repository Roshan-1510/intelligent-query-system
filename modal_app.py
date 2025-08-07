import modal
from main import app as fastapi_app  # Assumes main.py is in the same directory

# Debugging: List directory contents (optional, good for logs)
import os
print("DIR CONTENTS:", os.listdir())

# Declare the Modal app
app = modal.App(name="intelligent-query-system")

# ✅ Mount local project into the container
volume = modal.Mount.from_local_dir(".", remote_path="/app")

# Create image with requirements and volume mount
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install_from_requirements("requirements.txt")
)

@app.function(image=image, mounts=[volume])
@modal.asgi_app()
def fastapi_modal_app():
    return fastapi_app
