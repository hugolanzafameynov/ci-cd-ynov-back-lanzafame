# Backend Python FastAPI + MongoDB (CI/CD & Production)

## Présentation
Ce projet propose une API Python FastAPI sécurisée pour la gestion d'utilisateurs, avec une base MongoDB. Il est prêt pour :
- Le développement et les tests en local/CI avec Docker Compose (base MongoDB locale)
- Le déploiement en production sur une plateforme cloud avec MongoDB Atlas

## Fonctionnalités principales
- Authentification JWT (login)
- Gestion des utilisateurs (créer, voir, supprimer)
- Rôles (admin/user)
- Sécurité des routes (adminOnly)
- Versionnement d'API (`/v1/...`)
- Documentation automatique avec Swagger/OpenAPI accessible sur `/docs`

## Technologies utilisées
- **FastAPI** : Framework web moderne et rapide pour Python
- **Motor** : Driver MongoDB asynchrone pour Python
- **Pydantic** : Validation de données et sérialisation
- **PyJWT** : Gestion des tokens JWT
- **Passlib** : Hachage sécurisé des mots de passe
- **Uvicorn** : Serveur ASGI pour FastAPI
- **Pytest** : Framework de tests

## Structure du projet
```
.
├── src/
│   ├── controllers/        # Contrôleurs FastAPI
│   ├── middleware/         # Middlewares d'authentification/autorisation
│   ├── models/             # Modèles Pydantic
│   ├── database.py         # Configuration MongoDB avec Motor
│   └── init_admin.py       # Script Python pour initialiser l'admin
├── tests/
│   └── test_api.py         # Tests avec pytest
├── .env                    # Variables d'environnement locales (à créer)
├── .env.example            # Exemple de configuration d'environnement
├── Dockerfile              # Image Python pour l'API
├── docker-compose.yml      # Orchestration Docker (API + MongoDB pour tests)
├── server.py                 # Point d'entrée de l'API FastAPI
├── requirements.txt        # Dépendances Python
└── README.md               # Documentation
```

## Installation et démarrage

### Prérequis
- Docker et Docker Compose
- Python 3.11+ (pour le développement local sans Docker)

### Démarrage avec Docker Compose (recommandé)
1. Cloner le projet
2. Copier le fichier d'environnement et configurer les variables:
   ```bash
   cp .env.example .env
   ```
3. Démarrer les services :
   ```bash
   docker-compose up --build
   ```
4. L'API sera accessible sur `http://localhost:4000`
5. La documentation interactive sera sur `http://localhost:4000/docs`

## Gestion claire des environnements

### 1. Production (Vercel + MongoDB Atlas)
- **Variables d'environnement à configurer** :
  - `DATABASE_URL` = URL de MongoDB Atlas (ex: `mongodb+srv://user:pass@cluster.mongodb.net/dbname`)
  - `JWT_SECRET` = clé secrète forte pour JWT

### 2. Développement local & CI (tests)
- **Base de données** : MongoDB tourne en local dans un conteneur Docker
- **Initialisation automatique** : utilisateur admin est créé automatiquement avec les identifiants :
    - **Username** : `loise.fenoll@ynov.com`
    - **Password** : `PvdrTAzTeR247sDnAZBr`
- **Variables d'environnement** :
  - `DATABASE_URL` = URL de MongoDB local (ex: `mongodb://root:example@mongodb:27017/myapp?authSource=admin`)
  - `JWT_SECRET` = clé secrète forte pour JWT

Pour réinitialiser la base de données :
```bash
docker-compose down -v
docker-compose up --build
```

> **Astuce** : Pour passer de l’environnement de test/local à la production, il suffit de changer la variable `DATABASE_URL` (aucun changement de code nécessaire).

## Endpoints de l'API

### Routes publiques
- `GET /` - Root
- `POST /v1/users` - Créer un utilisateur
- `POST /v1/login` - Authentification

### Routes protégées (admin uniquement)
- `GET /v1/users` - Lister tous les utilisateurs
- `DELETE /v1/users/{user_id}` - Supprimer un utilisateur

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

## Tests
Exécuter les tests :
```bash
# Avec Docker
docker-compose exec api pytest tests/
```
**Tests d'authentification :**
- Login admin valide

**Tests de création d'utilisateur :**
- Création réussie d'un utilisateur
- Validation des champs requis (username, password)
- Exclusion du mot de passe dans les réponses

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

## Documentation interactive
Une fois l'API démarrée, vous pouvez accéder à :
- **Swagger UI** : `http://localhost:4000/docs`
- **ReDoc** : `http://localhost:4000/redoc`
