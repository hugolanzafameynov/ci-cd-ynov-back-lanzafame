# Backend Python FastAPI + MySQL (CI/CD & Production)

## Présentation
Ce projet propose une **API Python FastAPI sécurisée** pour la gestion d'utilisateurs, avec une base de données **MySQL**. Il est prêt pour :
- Le développement et les tests en local avec Docker Compose (base MySQL locale)
- Le déploiement en production avec **Aiven MySQL** (service cloud gratuit)

## Fonctionnalités principales
- **Authentification JWT** (login sécurisé)
- **Gestion des utilisateurs** (créer, voir, supprimer)
- **Système de rôles** (admin/user)
- **Sécurité des routes** (protection admin)
- **Documentation automatique** avec Swagger/OpenAPI sur `/docs`
- **Base de données MySQL** avec SQLAlchemy ORM

## Technologies utilisées
- **FastAPI** : Framework web moderne et rapide pour Python
- **SQLAlchemy** : ORM pour MySQL avec support asynchrone
- **Aiven MySQL** : Base de données MySQL cloud gratuite
- **PyJWT** : Gestion des tokens JWT
- **Passlib** : Hachage sécurisé des mots de passe (bcrypt)
- **Uvicorn** : Serveur ASGI pour FastAPI
- **Pytest** : Framework de tests

## Structure du projet
```
.
├── src/
│   ├── controllers/             
│   │   └── user_controller.py  # Contrôleur User
│   ├── middleware/         
│   │   └── auth.py             # Middlewares d'authentification
│   ├── models/
│   │   └── user.py             # Modèle User SQLAlchemy
│   ├── database.py             # Configuration MySQL avec SQLAlchemy
│   └── init_admin.py           # Initialisation de l'admin par default
├── tests/
│   └── test_api.py             # Tests avec pytest
├── .env                        # Variables d'environnement (à créer)
├── .env.example                # Template de configuration
├── .gitignore                  # Liste de fichiers ignorés par git
├── Dockerfile                  # Image Python pour l'API
├── docker-compose.yml          # Orchestration Docker (API + MySQL pour tests)
├── README.md                   # Cette documentation
├── requirements.txt            # Dépendances Python
└── server.py                   # Point d'entrée de l'API FastAPI

```

## Installation et démarrage

### Prérequis
- Docker et Docker Compose (pour le développement local)
- Python 3.10+ (optionnel, pour le développement local sans Docker)
- Compte Aiven gratuit (pour la production)

### Configuration

1. **Cloner le projet**
   ```bash
   git clone <votre-repo>
   cd ci-cd-back-ynov-lanzafame
   ```

2. **Configurer les variables d'environnement**
   ```bash
   cp .env.example .env
   ```

3. **Choisir votre mode de déploiement :**

#### Mode développement local (Docker)
```bash
# Dans .env, utilisez cette configuration :
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/myapp
JWT_SECRET=your-secret-key

# Démarrer avec Docker
docker-compose up --build
```

#### Mode production (Aiven MySQL)
```bash
# 1. Créez un compte sur https://aiven.io/ (300$ gratuit)
# 2. Créez un service MySQL (plan Hobbyist)
# 3. Copiez votre URL de connexion
# 4. Mettez à jour votre .env :
DATABASE_URL=mysql+aiomysql://avnadmin:VOTRE_PASSWORD@mysql-xxx.aivencloud.com:PORT/defaultdb
JWT_SECRET=your-very-secret-key

# 5. Créez l'utilisateur admin sur Aiven
python3 src/init_admin.py

# 6. Lancez le serveur
python3 server.py
```

## Endpoints de l'API

### Routes publiques
- `GET /` - Root
- `POST /v1/users` - Créer un utilisateur
- `POST /v1/login` - Authentification

### Routes protégées (admin uniquement)
- `GET /v1/users` - Lister tous les utilisateurs
- `DELETE /v1/users/{user_id}` - Supprimer un utilisateur

## Utilisateur administrateur par défaut

L'application crée automatiquement un utilisateur administrateur lors du premier démarrage :

### Identifiants admin par défaut
- **Username** : `loise.fenoll@ynov.com`
- **Password** : `PvdrTAzTeR247sDnAZBr`

## Exemple de requêtes API
- **Créer un utilisateur (public)**
  ```http
  POST /v1/users
  Content-Type: application/json
  {
    "username": "nouveluser",
    "password": "motdepasse",
    "name": "Prénom",
    "last_name": "Nom"
  }
  ```
- **Login**
  ```http
  POST /v1/login
  Content-Type: application/json
  {
    "username": "loise.fenoll@ynov.com",
    "password": "PvdrTAzTeR247sDnAZBr"
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

### Accès à l'API
- **API** : `http://localhost:4000`
- **Documentation interactive** : `http://localhost:4000/docs`
- **Alternative ReDoc** : `http://localhost:4000/redoc`
