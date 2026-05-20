import pytest
from app import create_app
from app.database import db as _db


@pytest.fixture
def app():
    application = create_app()
    application.config["TESTING"] = True
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_listar_usuarios_vacio(client):
    response = client.get("/usuarios")
    assert response.status_code == 200
    assert response.get_json() == []


def test_crear_usuario(client):
    payload = {"nombre": "Juan Perez", "email": "juan@example.com"}
    response = client.post("/usuarios", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["nombre"] == "Juan Perez"
    assert data["email"] == "juan@example.com"
    assert data["activo"] is True


def test_crear_usuario_sin_datos(client):
    response = client.post("/usuarios", json={})
    assert response.status_code == 400


def test_crear_usuario_email_duplicado(client):
    payload = {"nombre": "Juan", "email": "juan@example.com"}
    client.post("/usuarios", json=payload)
    response = client.post("/usuarios", json=payload)
    assert response.status_code == 409


def test_obtener_usuario(client):
    client.post("/usuarios", json={"nombre": "Ana", "email": "ana@example.com"})
    response = client.get("/usuarios/1")
    assert response.status_code == 200
    assert response.get_json()["email"] == "ana@example.com"


def test_obtener_usuario_no_existe(client):
    response = client.get("/usuarios/999")
    assert response.status_code == 404


def test_actualizar_usuario(client):
    client.post("/usuarios", json={"nombre": "Carlos", "email": "carlos@example.com"})
    response = client.put("/usuarios/1", json={"nombre": "Carlos Actualizado"})
    assert response.status_code == 200
    assert response.get_json()["nombre"] == "Carlos Actualizado"


def test_eliminar_usuario(client):
    client.post("/usuarios", json={"nombre": "Luis", "email": "luis@example.com"})
    response = client.delete("/usuarios/1")
    assert response.status_code == 200
    assert client.get("/usuarios/1").status_code == 404
