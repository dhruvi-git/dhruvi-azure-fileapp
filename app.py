import os
from flask import Flask, render_template, request, redirect, url_for, flash
from azure.storage.blob import BlobServiceClient, ContentSettings

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

# These come from App Service > Configuration > Application settings (set in Azure Portal)
CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.environ.get("AZURE_STORAGE_CONTAINER", "dhruvi-files")


def get_container_client():
    """Returns a client for the configured container, creating it if needed."""
    if not CONNECTION_STRING:
        raise RuntimeError(
            "AZURE_STORAGE_CONNECTION_STRING is not set. "
            "Set it in Azure App Service > Configuration > Application settings."
        )
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    try:
        container_client.create_container()
    except Exception:
        # Container already exists — safe to ignore
        pass
    return container_client


@app.route("/")
def index():
    error = None
    blobs = []
    try:
        container_client = get_container_client()
        for blob in container_client.list_blobs():
            blob_client = container_client.get_blob_client(blob.name)
            blobs.append({
                "name": blob.name,
                "size_kb": round((blob.size or 0) / 1024, 2),
                "last_modified": blob.last_modified,
                "url": blob_client.url,
            })
        blobs.sort(key=lambda b: b["last_modified"], reverse=True)
    except Exception as e:
        error = str(e)

    return render_template(
        "index.html",
        blobs=blobs,
        container=CONTAINER_NAME,
        error=error,
    )


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Please choose a file to upload.")
        return redirect(url_for("index"))

    try:
        container_client = get_container_client()
        blob_client = container_client.get_blob_client(file.filename)
        blob_client.upload_blob(
            file.stream,
            overwrite=True,
            content_settings=ContentSettings(
                content_type=file.content_type or "application/octet-stream"
            ),
        )
        flash(f"'{file.filename}' uploaded successfully!")
    except Exception as e:
        flash(f"Upload failed: {e}")

    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # Local dev only. Azure App Service uses gunicorn (see startup command).
    app.run(debug=True, host="0.0.0.0", port=8000)
