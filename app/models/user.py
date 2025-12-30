from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db   # ✅ importa o db único centralizado em app/extensions.py
from flask_login import UserMixin  # 👈 adiciona suporte ao Flask-Login

# -----------------------------
# 👤 Usuário (Admin / Login)
# -----------------------------
class User(db.Model, UserMixin):   # 👈 herda de UserMixin
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="admin")  # pode ser "admin", "user", etc.
    nome = db.Column(db.String(100), nullable=True)

    # Define a senha (gera o hash seguro)
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    # Verifica se a senha informada confere com o hash
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
