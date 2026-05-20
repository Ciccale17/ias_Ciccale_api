from flask import Blueprint, jsonify, request
from .models import Usuario
from .database import db

usuarios_bp = Blueprint("usuarios", __name__)


# Healthcheck
@usuarios_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "mensaje": "API funcionando correctamente"}), 200


# Listar todos los usuarios
@usuarios_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([u.to_dict() for u in usuarios]), 200


# Obtener un usuario por ID
@usuarios_bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
def obtener_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(usuario.to_dict()), 200


# Crear un usuario
@usuarios_bp.route("/usuarios", methods=["POST"])
def crear_usuario():
    data = request.get_json()

    if not data or not data.get("nombre") or not data.get("email"):
        return jsonify({"error": "nombre y email son obligatorios"}), 400

    if Usuario.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "El email ya existe"}), 409

    nuevo = Usuario(
        nombre=data["nombre"],
        email=data["email"],
        activo=data.get("activo", True),
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201


# Actualizar un usuario
@usuarios_bp.route("/usuarios/<int:usuario_id>", methods=["PUT"])
def actualizar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json()
    if "nombre" in data:
        usuario.nombre = data["nombre"]
    if "email" in data:
        usuario.email = data["email"]
    if "activo" in data:
        usuario.activo = data["activo"]

    db.session.commit()
    return jsonify(usuario.to_dict()), 200


# Eliminar un usuario
@usuarios_bp.route("/usuarios/<int:usuario_id>", methods=["DELETE"])
def eliminar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200
