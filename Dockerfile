# Utilise l'image officielle Python
FROM python:3.11-slim

# Crée le dossier de l'app
WORKDIR /usr/src/app

# Copie les fichiers requirements
COPY requirements.txt ./

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste du code
COPY . .

# Expose le port de l'API
EXPOSE 4000

# Démarre l'API avec uvicorn
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "4000"]
