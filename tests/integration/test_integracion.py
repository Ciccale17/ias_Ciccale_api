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


def test_flujo_completo_abm(client):
    """Prueba el flujo completo: crear, leer, actualizar y eliminar un usuario."""

    # Crear
    resp = client.post("/usuarios", json={"nombre": "Test User", "email": "test@test.com"})
    assert resp.status_code == 201
    usuario_id = resp.get_json()["id"]

    # Leer
    resp = client.get(f"/usuarios/{usuario_id}")
    assert resp.status_code == 200
    assert resp.get_json()["nombre"] == "Test User"

    # Actualizar
    resp = client.put(f"/usuarios/{usuario_id}", json={"nombre": "Test Modificado", "activo": False})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["nombre"] == "Test Modificado"
    assert data["activo"] is False

    # Listar
    resp = client.get("/usuarios")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1

    # Eliminar
    resp = client.delete(f"/usuarios/{usuario_id}")
    assert resp.status_code == 200

    # Verificar eliminación
    resp = client.get(f"/usuarios/{usuario_id}")
    assert resp.status_code == 404


def test_multiples_usuarios(client):
    """Prueba crear varios usuarios y listarlos."""
    usuarios = [
        {"nombre": "Usuario 1", "email": "u1@test.com"},
        {"nombre": "Usuario 2", "email": "u2@test.com"},
        {"nombre": "Usuario 3", "email": "u3@test.com"},
    ]
    for u in usuarios:
        resp = client.post("/usuarios", json=u)
        assert resp.status_code == 201

    resp = client.get("/usuarios")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 3


def test_healthcheck_disponible(client):
    """Verifica que el healthcheck responde correctamente."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
