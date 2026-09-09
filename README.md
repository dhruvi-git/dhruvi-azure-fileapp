# Dhruvi Jain — Azure Blob Storage File Manager

A simple Flask web app that lists and uploads files to an Azure Blob Storage
container. Deployed on Azure App Service (PaaS) via GitHub deployment.

## Architecture
User -> Web App (Azure App Service) -> Azure Blob Storage -> Files/Blobs

## Local run
```bash
python -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install -r requirements.txt

export AZURE_STORAGE_CONNECTION_STRING="<your-connection-string>"
export AZURE_STORAGE_CONTAINER="dhruvi-files"

python app.py
# visit http://localhost:8000
```

## Azure deployment
See the full step-by-step guide provided separately. In short:
1. Create a Storage Account + Blob container in Azure Portal.
2. Create an App Service (Python 3.11, Linux, Free/Basic tier).
3. In App Service > Configuration, add app settings:
   - `AZURE_STORAGE_CONNECTION_STRING`
   - `AZURE_STORAGE_CONTAINER`
4. In App Service > Deployment Center, connect this GitHub repo for CI/CD.
5. Set Startup Command: `gunicorn --bind=0.0.0.0 --timeout 600 app:app`
