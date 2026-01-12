from flask import Blueprint
from .atas.atas import atas_bp
from .cartas.cartas import cartas_bp
from .certificados.certificados import certificados_bp

documentos_bp = Blueprint("documentos", __name__, url_prefix="/documentos")

documentos_bp.register_blueprint(atas_bp)
documentos_bp.register_blueprint(cartas_bp)
documentos_bp.register_blueprint(certificados_bp)

__all__ = ["documentos_bp"]
