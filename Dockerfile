# Utilise l'image officielle Node.js
FROM node:22

# Crée le dossier de l'app
WORKDIR /usr/src/app

# Copie les fichiers package.json et package-lock.json
COPY package*.json ./

# Installe les dépendances
RUN npm install

# Copie le reste du code
COPY . .

# Expose le port de l'API
EXPOSE 4000

# Démarre l'API
CMD [ "node", "server.js" ]
