import os

# Для отладки
from dotenv import load_dotenv
load_dotenv()


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET')


class ProdConfig(Config):
    DEBUG = False
    TESTING = False


class DevConfig(Config):
    DEBUG = True
    TESTING = False
