from .auth import auth_bp
from .dashboard import dashboard_bp
from .event import event_bp
from .financeiro import financeiro_bp
from .member import member_bp
from .patrimonio import patrimonio_bp
from .admin import admin_bp 

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "event_bp",
    "financeiro_bp",
    "member_bp",
    "patrimonio_bp",
    "admin_bp",
]
