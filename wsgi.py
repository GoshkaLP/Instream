from app import create_app

from config import DevConfig, ProdConfig


app = create_app(ProdConfig)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8087, use_reloader=False)