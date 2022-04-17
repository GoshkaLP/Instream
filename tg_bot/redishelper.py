import redis
import os

# Для отладки
# from dotenv import load_dotenv
# load_dotenv()

REDIS_HOST = os.getenv('HOST')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

redis_con = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    db=0,
    password=REDIS_PASSWORD
)
