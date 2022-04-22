from telethon import TelegramClient
from telethon.tl.types import UpdateGroupCall, UpdateGroupCallParticipants
from io import BytesIO

from datetime import datetime
from dateutil import tz

from db import session_scope, redis_con

from models import Channels, AnnouncedStreams, CurrentStreams, FinishedStreams

import os

# Для отладки
# from dotenv import load_dotenv
# load_dotenv()

from_zone = tz.gettz('UTC')


api_id = int(os.getenv('TG_API_ID'))
api_hash = os.getenv('TG_API_HASH')
client = TelegramClient('anon', api_id, api_hash)


async def tg_channel_data(channel_id):
    """
    Метод для получения информации о канале
    """
    channel_entity = await client.get_entity(channel_id)
    name = channel_entity.title
    username = channel_entity.username

    photo = BytesIO()
    participants = await client.get_participants(int(channel_id), limit=0)
    await client.download_profile_photo(int(channel_id), file=photo)
    if photo.getbuffer().nbytes:
        photo = photo.getvalue()
    else:
        photo = None
    subs_count = participants.total
    return name, username, subs_count, photo


# Методы для работы с базой данных
def get_channel_info(channel_id):
    """
    Метод для получения информации о канале из базы данных
    """
    with session_scope() as session:
        res = session.query(Channels).filter_by(id=channel_id).first()
        return res


def add_channel_info(channel_id, name, username, subs_count, photo):
    """
    Метод для добавления информации о канале в базу данных
    """
    with session_scope() as session:
        if not get_channel_info(channel_id):
            new_channel = Channels(
                id=channel_id,
                name=name,
                username=username,
                subscribers=subs_count,
                photo=photo
            )
            session.add(new_channel)


def get_scheduled_stream(stream_id):
    """
    Метод для получения запланированного стрима
    """
    with session_scope() as session:
        res = session.query(AnnouncedStreams).filter_by(id=stream_id).first()
        return res


def add_scheduled_stream(channel_id, stream_id, scheduled_date):
    """
    Метод для добавления запланированного стрима
    """
    with session_scope() as session:
        if not get_scheduled_stream(stream_id):
            new_announced_stream = AnnouncedStreams(
                id=stream_id,
                channel_id=channel_id,
                scheduled_date=scheduled_date
            )
            session.add(new_announced_stream)


def delete_scheduled_stream(stream_id):
    """
    Метод для удаления запланированного стрима
    """
    with session_scope() as session:
        if get_scheduled_stream(stream_id):
            session.query(AnnouncedStreams).filter_by(id=stream_id).delete()


def get_started_stream(stream_id):
    """
    Метод для получения начатого стрима
    """
    with session_scope() as session:
        res = session.query(CurrentStreams).filter_by(id=stream_id).first()
        return res


def add_started_stream(channel_id, stream_id, start_date, scheduled):
    """
    Метод для добавления начатого стрима
    """
    with session_scope() as session:
        if not get_started_stream(stream_id):
            new_started_stream = CurrentStreams(
                id=stream_id,
                channel_id=channel_id,
                start_date=start_date,
                scheduled=scheduled
            )
            session.add(new_started_stream)


def delete_started_stream(stream_id):
    """
    Метод для удаления начатого стрима
    """
    with session_scope() as session:
        if get_started_stream(stream_id):
            session.query(CurrentStreams).filter_by(id=stream_id).delete()


def get_finished_stream(stream_id):
    """
    Метод для получения завершенного стрима
    """
    with session_scope() as session:
        res = session.query(FinishedStreams).filter_by(id=stream_id).first()
        return res


def add_finished_stream(channel_id, stream_id, start_date, end_date, duration, watchers, scheduled):
    """
    Метод для добавления завершенного стрима
    """
    with session_scope() as session:
        if not get_finished_stream(stream_id):
            new_finished_stream = FinishedStreams(
                id=stream_id,
                channel_id=channel_id,
                start_date=start_date,
                end_date=end_date,
                duration=duration,
                viewers_count=watchers,
                scheduled=scheduled
            )
            session.add(new_finished_stream)


# Методы для работы с Redis
def add_stream_viewers(stream_id):
    """
    Метод для добавления начатого стрима в Redis с начальными значениями
    """
    key = 'stream:{}'.format(stream_id)
    if not redis_con.hgetall(key):
        redis_con.hset(key, 'current_viewers', 0)
        redis_con.hset(key, 'max_viewers', 0)


def update_viewers_count(stream_id, incr_val):
    """
    Метод для обновления кол-ва зрителей начатого стрима в Redis
    """
    key = 'stream:{}'.format(stream_id)
    if redis_con.hgetall(key):
        redis_con.hincrby(key, 'current_viewers', incr_val)
        current_viewers = redis_con.hget(key, 'current_viewers')
        max_viewers = redis_con.hget(key, 'max_viewers')
        if current_viewers > max_viewers:
            redis_con.hset(key, 'max_viewers', current_viewers)


def get_max_viewers_count(stream_id):
    """
    Метод для получения максимального числа зрителей начатого стрима из Redis
    """
    key = 'stream:{}'.format(stream_id)
    if redis_con.hgetall(key):
        return int(redis_con.hget(key, 'max_viewers'))


def delete_stream_viewers(stream_id):
    """
    Метод для удаления начатого стрима из Redis
    """
    key = 'stream:{}'.format(stream_id)
    if redis_con.hgetall(key):
        redis_con.delete(key)


async def handler(update):
    """
    Основной метод обработчик событий о стриме и его участниках
    """
    channel_id = None
    # Если прилетел интересующий нас ивент
    if isinstance(update, UpdateGroupCall) or isinstance(update, UpdateGroupCallParticipants):
        update = update.to_dict()
        # print(update)

        call = update.get('call')
        stream_id = str(call.get('id'))
        if update.get('chat_id'):
            channel_id = str(update.get('chat_id'))
            name, username, subscribers, photo = await tg_channel_data(int(channel_id))
            add_channel_info(channel_id, name, username, subscribers, photo)

        # Обработка ивентов со стримами
        if update.get('_') == 'UpdateGroupCall':

            # Если ивент связан с окончанием трансляции
            if call.get('_') == 'GroupCallDiscarded':
                # если трансляция была запланированной, то удаляем запись об этой трансляции
                if get_scheduled_stream(stream_id):
                    delete_scheduled_stream(stream_id)
                # если же трансляция не была запланированной, то перемещаем трансляцию в заверешенную и записываем
                # кол-во зрителей, длительность и дату окончания
                else:
                    if get_started_stream(stream_id):
                        duration = call.get('duration')
                        watchers_count = get_max_viewers_count(stream_id)
                        end_date = datetime.now(tz=from_zone)
                        started_stream = get_started_stream(stream_id)
                        delete_started_stream(stream_id)
                        add_finished_stream(
                            channel_id=channel_id,
                            stream_id=stream_id,
                            start_date=started_stream.start_date,
                            end_date=end_date,
                            duration=duration,
                            watchers=watchers_count,
                            scheduled=started_stream.scheduled
                        )
                        delete_stream_viewers(stream_id)

            # Если трансляция запланированная
            elif call.get('schedule_date'):
                scheduled_date = call.get('schedule_date')
                add_scheduled_stream(channel_id, stream_id, scheduled_date)

            # Если трансляция началась
            elif call.get('schedule_date') is None:
                # если данная трансляция была запланированной, то перемащаем запись, иначе просто создаем новую
                # с датой начала
                scheduled = False
                start_date = datetime.now(tz=from_zone)
                if get_scheduled_stream(stream_id):
                    scheduled = True
                    delete_scheduled_stream(stream_id)
                add_started_stream(channel_id=channel_id, stream_id=stream_id, scheduled=scheduled,
                                   start_date=start_date)
                add_stream_viewers(stream_id)

        # Обработка ивентов с участниками стрима
        elif update.get('_') == 'UpdateGroupCallParticipants':
            if get_started_stream(stream_id):
                participant = update.get('participants')[0]
                if participant.get('just_joined'):
                    update_viewers_count(stream_id, 1)
                elif participant.get('left'):
                    update_viewers_count(stream_id, -1)


client.add_event_handler(handler)
client.start()
client.run_until_disconnected()

# async def main():
#     photo = BytesIO()
#     await client.download_profile_photo('goshkalp_test', file=photo)
#     print(photo.getbuffer().nbytes)
#
# with client:
#     client.loop.run_until_complete(main())

