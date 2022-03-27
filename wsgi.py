from app import create_app
from app.views.extensions.tg_module import client
from multiprocessing import Process

from config import DevConfig, ProdConfig


def start_tg_client():
    client.start()
    client.run_until_disconnected()


# Не забыть поменять на ProdConfig
app = create_app(ProdConfig)

if __name__ == "__main__":
    p = Process(target=start_tg_client)
    p.start()
    app.run(host='0.0.0.0', port=8080, use_reloader=False)
    p.join()
