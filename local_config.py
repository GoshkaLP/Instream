import os
from sqlalchemy import create_engine

# Для отладки
from dotenv import load_dotenv
load_dotenv()

# Конфиг с информацией об IP адресе сервера, на котором работает проект с созданием подключения к PSQL базе данных
POSTGRES_HOST = '23.105.226.217'
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

SQL_ENGINE = create_engine("postgresql://{user}:{password}@{host}:5433/{db}".format(
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    db=POSTGRES_DB
),
    pool_recycle=3600)
