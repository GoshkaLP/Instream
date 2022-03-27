# Создание объекта приложения
from flask import Flask

from app.views import node

from app.views.extensions.tg_module import client

# from .views.models import db
#
# from .views.tasks import scheduler
#
# from .views.extensions.protection_ext import mail


def create_app(app_config=None):
    app = Flask(__name__, instance_relative_config=False)

    if app_config is None:
        return None

    app.config.from_object(app_config)

    app.register_blueprint(node)

    return app
