import os
from app import create_app

# Decide qual configuração usar
config_class = "config.ProductionConfig" if os.environ.get("FLASK_ENV") == "production" else "config.DevelopmentConfig"

app = create_app(config_class)

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
