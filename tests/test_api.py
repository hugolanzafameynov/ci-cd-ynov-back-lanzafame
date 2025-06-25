import pytest
import time
from fastapi.testclient import TestClient
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

def get_client():
    """Créer un nouveau client pour chaque test"""
    return TestClient(app)

# Tests de base
def test_root_endpoint():
    """Test de l'endpoint racine"""
    client = get_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API Backend Ynov - Python FastAPI"}

def test_database_connection():
    """Test de connexion à la base de données"""
    client = get_client()
    response = client.get("/v1/users")
    # Doit retourner 401/403 (pas de token) et pas 500 (erreur DB)
    assert response.status_code in [401, 403]

# Tests d'authentification
def test_login_admin_success():
    """Test de connexion admin"""
    client = get_client()
    response = client.post("/v1/login", json={
        "username": "loise.fenoll@ynov.com",
        "password": "PvdrTAzTeR247sDnAZBr"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data

def test_login_nonexistent_user():
    """Test de connexion avec utilisateur inexistant"""
    client = get_client()
    response = client.post("/v1/login", json={
        "username": "usernotexist",
        "password": "anypass"
    })
    assert response.status_code == 401

# Tests de création d'utilisateur
def test_create_user_success():
    """Test de création d'utilisateur réussie"""
    client = get_client()
    unique_username = f"testuser_{int(time.time() * 1000)}"
    response = client.post("/v1/users", json={
        "username": unique_username,
        "password": "testpass",
        "name": "Test",
        "lastName": "User"
    })
    assert response.status_code == 201

def test_create_user_no_username():
    """Test de création sans username"""
    client = get_client()
    response = client.post("/v1/users", json={
        "password": "testpass"
    })
    assert response.status_code in [400, 422]

def test_create_user_no_password():
    """Test de création sans password"""
    client = get_client()
    response = client.post("/v1/users", json={
        "username": "usernopass"
    })
    assert response.status_code in [400, 422]

# Tests de récupération d'utilisateurs
def test_get_users_no_auth():
    """Test de récupération sans authentification"""
    client = get_client()
    response = client.get("/v1/users")
    assert response.status_code in [401, 403]

def test_get_users_admin_success():
    """Test de récupération avec admin"""
    client = get_client()
    # Se connecter en tant qu'admin
    login_response = client.post("/v1/login", json={
        "username": "loise.fenoll@ynov.com",
        "password": "PvdrTAzTeR247sDnAZBr"
    })
    assert login_response.status_code == 200
    
    token = login_response.json().get("access_token") or login_response.json().get("token")
    response = client.get("/v1/users", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert "utilisateurs" in data
    assert isinstance(data["utilisateurs"], list)

# Tests de suppression d'utilisateur
def test_delete_user_no_auth():
    """Test de suppression sans authentification"""
    client = get_client()
    response = client.delete("/v1/users/507f1f77bcf86cd799439011")  # ID fictif
    assert response.status_code in [401, 403]

def test_delete_nonexistent_user():
    """Test de suppression d'utilisateur inexistant"""
    client = get_client()
    # Se connecter en tant qu'admin
    login_response = client.post("/v1/login", json={
        "username": "loise.fenoll@ynov.com",
        "password": "PvdrTAzTeR247sDnAZBr"
    })
    assert login_response.status_code == 200
    
    token = login_response.json().get("token")
    response = client.delete("/v1/users/507f1f77bcf86cd799439011", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
