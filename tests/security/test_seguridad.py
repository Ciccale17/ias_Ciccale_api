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


def test_no_acepta_datos_nulos(client):
    """Verifica que no se acepten datos nulos o incompletos."""
    resp = client.post("/usuarios", json={"nombre": "", "email": ""})
    assert resp.status_code == 400


def test_respuesta_json(client):
    """Verifica que todos los endpoints devuelven JSON."""
    resp = client.get("/health")
    assert resp.content_type == "application/json"

    resp = client.get("/usuarios")
    assert resp.content_type == "application/json"


def test_usuario_no_encontrado_retorna_404(client):
    """Verifica que se retorna 404 para recursos inexistentes."""
    resp = client.get("/usuarios/99999")
    assert resp.status_code == 404


def test_no_permite_email_duplicado(client):
    """Verifica que no se pueden crear usuarios con emails duplicados."""
    payload = {"nombre": "User", "email": "duplicado@test.com"}
    client.post("/usuarios", json=payload)
    resp = client.post("/usuarios", json=payload)
    assert resp.status_code == 409


def test_put_usuario_inexistente(client):
    """Verifica que actualizar un usuario inexistente devuelve 404."""
    resp = client.put("/usuarios/99999", json={"nombre": "Nadie"})
    assert resp.status_code == 404


def test_delete_usuario_inexistente(client):
    """Verifica que eliminar un usuario inexistente devuelve 404."""
    resp = client.delete("/usuarios/99999")
    assert resp.status_code == 404
