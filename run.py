import os
from app import create_app
from config import get_config   # ✅ importa a função que decide o ambiente

app = create_app(get_config())

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
