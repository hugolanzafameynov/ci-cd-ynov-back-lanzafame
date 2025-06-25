const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const mongoose = require('mongoose');
const { getAllUsers, deleteUser, login, addUser } = require('./src/controller/userController');
const auth = require('./src/middleware/auth');
const adminOnly = require('./src/middleware/adminOnly');

dotenv.config();

const app = express();
const databaseUrl = process.env.DATABASE_URL;
const port = 4000;

app.use(cors());
app.use(express.json());

if (mongoose.connection.readyState === 0) {
  const mongoConfig = {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  };

  mongoose.connect(databaseUrl, mongoConfig)
    .then(() => {
      console.log('Connected to MongoDB');
    })
    .catch((err) => {
      console.error('MongoDB connection error:', err.message);
    });
}

// Route POST pour ajouter un user (publique)
app.post('/v1/users', addUser);
// Route GET pour récupérer tous les users (admin seulement)
app.get('/v1/users', auth, adminOnly, getAllUsers);
// Route DELETE pour supprimer un user (admin seulement)
app.delete('/v1/users/:id', auth, adminOnly, deleteUser);
// Route POST pour login
app.post('/v1/login', login);

// Démarrage du serveur (uniquement en local/Docker, pas sur Vercel/Serverless)
if (require.main === module) {
  app.listen(port, () => {
    console.log(`Serveur démarré sur http://localhost:${port}`);
  });
}

module.exports = app; // Exporter l'application pour les tests toto