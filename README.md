# Backend Node.js + MongoDB (CI/CD & Production)

## Présentation
Ce projet propose une API Node.js sécurisée pour la gestion d’utilisateurs, avec une base MongoDB. Il est prêt pour :
- Le développement et les tests en local/CI avec Docker Compose (base MongoDB locale)
- Le déploiement en production sur Vercel avec MongoDB Atlas (base cloud)

## Fonctionnalités principales
- Authentification JWT (login)
- Gestion des utilisateurs (créer, voir, supprimer)
- Rôles (admin/user)
- Sécurité des routes (adminOnly)
- Versionnement d’API (`/v1/...`)

## Structure du projet
```
.
├── src/
│   ├── controller/         # Contrôleurs Express
│   ├── middleware/         # Middlewares d’authentification/autorisation
│   ├── model/              # Modèles Mongoose
│   └── init-admin.js       # Script Node.js pour initialiser l'admin (mot de passe hashé)
├── .env                    # Variables d’environnement locales (à créer)
├── .env.exemple            # Exemple de configuration d’environnement
├── Dockerfile              # Image Node.js pour l’API
├── docker-compose.yml      # Orchestration Docker (API + MongoDB pour tests)
├── server.js               # Point d’entrée de l’API (reste à la racine)
├── package.json            # Dépendances et scripts Node.js
├── package-lock.json       # Lockfile npm
└── README.md               # Documentation
```

## Gestion claire des environnements

### 1. Production (Vercel + MongoDB Atlas)
- **Déploiement** : L’API Node.js est déployée sur Vercel (pas de base MongoDB dans le déploiement)
- **Variables d’environnement à configurer sur Vercel** :
  - `DATABASE_URL` = URL de ta base MongoDB Atlas (ex: `mongodb+srv://...`)
  - `JWT_SECRET` = un secret fort
- **Comportement** : L’API se connecte automatiquement à la base cloud grâce à `DATABASE_URL`.
- **Port** : L’application écoute sur le port imposé par la plateforme (Vercel/Heroku) ou sur 4000 par défaut.

### 2. Développement local & CI (tests)
- **Lancement** :
  ```bash
  docker-compose up --build
  ```
  Pour arrêter proprement les conteneurs :
  ```bash
  docker-compose down
  ```
  (Ajoute `-v` pour supprimer aussi les volumes (les données de la db) : `docker-compose down -v`)
- **Base de test** : MongoDB tourne en local dans un conteneur Docker.
- **Initialisation automatique de l’admin** :
  - Un service `init-admin` dans `docker-compose.yml` exécute automatiquement le script `init-admin.js` après le démarrage de MongoDB.
  - L’admin (`admin` / `admin123`) est créé avec un mot de passe hashé, compatible avec l’API.
- **Variables d’environnement dans `.env`** :
  - `DATABASE_URL=mongodb://root:example@mongodb:27017/myapp?authSource=admin`
  - `JWT_SECRET=secret`
- **Port** : Le port d’écoute de l’API est fixé à 4000 dans le code et dans `docker-compose.yml` (`ports: ["4000:4000"]`).
- **CI/CD** : Le workflow GitHub Actions (`.github/workflows/ci.yml`) utilise aussi cette base locale pour exécuter les tests automatiquement.

> **Astuce** : Pour passer de l’environnement de test/local à la production, il suffit de changer la variable `DATABASE_URL` (aucun changement de code nécessaire).

## Initialisation de l’admin
- L’utilisateur admin (`admin` / `admin123`) est créé automatiquement à chaque démarrage de l’environnement local/CI grâce au service `init-admin`.
- Si l’admin existe déjà, le script ne fait rien.
- Pour forcer la réinitialisation, supprime le volume de données MongoDB :
  ```bash
  docker-compose down -v
  docker-compose up --build
  ```

## Exemple de requêtes API
- **Créer un utilisateur (public)**
  ```http
  POST /v1/users
  Content-Type: application/json
  {
    "username": "nouveluser",
    "password": "motdepasse",
    "name": "Prénom",
    "lastName": "Nom"
  }
  ```
- **Login**
  ```http
  POST /v1/login
  Content-Type: application/json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Voir tous les utilisateurs** (admin seulement)
  ```http
  GET /v1/users
  Authorization: Bearer <token>
  ```
- **Supprimer un utilisateur** (admin seulement)
  ```http
  DELETE /v1/users/:id
  Authorization: Bearer <token>
  ```

## Sécurité
- Les mots de passe sont hashés (bcrypt)
- Les routes sensibles sont protégées par JWT et vérification du rôle admin
- Les champs sensibles (`password`, `__v`) sont exclus des réponses API
- Les routes sont versionnées (`/v1/...`)

## Tests automatisés

### Lancer les tests
```bash
npm test
```

### Tests inclus
L'API dispose d'une suite de tests complète couvrant tous les endpoints :

**Tests d'authentification :**
- Login admin valide
- Login avec mauvais mot de passe
- Login avec utilisateur inexistant

**Tests de création d'utilisateur :**
- Création réussie d'un utilisateur
- Validation des champs requis (username, password)
- Gestion des utilisateurs en double
- Exclusion du mot de passe dans les réponses
- Support des caractères spéciaux dans le username

**Tests de récupération d'utilisateurs :**
- Accès refusé sans authentification
- Accès refusé pour les utilisateurs non-admin
- Récupération réussie avec token admin
- Vérification que les mots de passe ne sont jamais exposés

**Tests de suppression d'utilisateur :**
- Suppression réussie avec token admin
- Accès refusé sans token
- Accès refusé pour les utilisateurs non-admin
- Gestion des utilisateurs inexistants
- Protection contre l'auto-suppression de l'admin

### CI/CD avec GitHub Actions
Les tests sont exécutés automatiquement à chaque push ou pull request via GitHub Actions, garantissant la qualité du code avant déploiement.
