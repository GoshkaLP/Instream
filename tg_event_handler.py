from telethon import TelegramClient, events
from telethon.tl.types import UpdateGroupCall, UpdateGroupCallParticipants

from datetime import datetime
from dateutil import tz

from dbhelper import session_scope
from models import Channels, AnnouncedStreams, CurrentStreams, FinishedStreams

from redishelper import redis_con

from_zone = tz.gettz('UTC')
to_zone = tz.tzlocal()


def convert_to_local_time(utc_date):
    # utc = datetime(*utc_date, tzinfo=from_zone)
    local_time = utc_date.astimezone(to_zone)
    return local_time.strftime('%d-%m-%y %H:%M')


# Remember to use your own values from my.telegram.org!
api_id = 447892
api_hash = 'a7f34f4cffe1b1b0bf99a2a2a54ec969'
client = TelegramClient('anon', api_id, api_hash)


# async def main():
#     # Getting information about yourself
#     # me = await client.get_me()
#     async with client:
#         while True:
#             print('Working...')
#             dialogs = await client.get_dialogs()
#             for dialog in dialogs:
#                 if dialog.is_channel:
#                     dialog_entity = dialog.entity.to_dict()
#                     channel_name = dialog.name
#                     username = dialog_entity.get('username')
#                     subs_count = dialog_entity.get('participants_count')
#                     print('Название канала: {}'.format(channel_name))
#                     print('Ссылка на канал: t.me/{}'.format(username))
#                     print('Количество подписчиков: {}'.format(subs_count))
#
#                     photo = io.BytesIO()
#                     has_photo = await client.download_profile_photo(dialog.id, file=photo)
#                     # print(photo.getbuffer().nbytes)
#                     if has_photo:
#                         print(has_photo.read())
#
#
#                     messages = await client.get_messages(dialog.id, limit=10)
#
#                     stream_founded = False
#
#                     for message in messages:
#                         message = message.to_dict()
#                         action = message.get('action')
#                         # print(action)
#                         if action:
#                             # not scheduled stream
#                             if action.get('_') == 'MessageActionGroupCall':
#                                 stream_founded = True
#                                 duration = action.get('duration')
#                                 # stream ended
#                                 if isinstance(duration, int):
#                                     print('Стрим прошел с длительностью {} секунд'.format(duration))
#                                     break
#                                 # stream is going
#                                 else:
#                                     print('В данный момент идет стрим')
#                                     break
#                             # scheduled stream
#                             elif action.get('_') == 'MessageActionGroupCallScheduled':
#                                 stream_founded = True
#                                 schedule_date = action.get('schedule_date')
#                                 schedule_local_date = convert_to_local_time(schedule_date)
#                                 print('На {} по МСК запланирован стрим!'.format(schedule_local_date))
#
#                     if not stream_founded:
#                         print('На данный момент стримов нет!')
#
#                     print('-----------------')
#                     await asyncio.sleep(2)
#             print('Sleeping...')
#             await asyncio.sleep(50000)

# with client:
#     client.loop.run_until_complete(main())

# loop = asyncio.get_event_loop()
# loop.create_task(main())
# try:
#     loop.run_forever()
# except KeyboardInterrupt:
#     pass

# @client.on(events.NewMessage)
# async def my_event_handler(event):
#     print(event)


async def tg_channel_data(channel_id):
    channel_entity = await client.get_entity(channel_id)
    name = channel_entity.title
    username = channel_entity.username
    subs_count = channel_entity.participants_count
    # photo = channel_entity.photo
    print(name, username, subs_count)
    return name, username, subs_count


def add_channel_info(channel_id, name, username, subs_count, photo):
    new_channel = Channels(
        id=channel_id,
        name=name,
        username=username,
        subscribers=subs_count
    )
    with session_scope() as session:
        session.add(new_channel)


def get_channel_info(channel_id):
    with session_scope() as session:
        res = session.query(Channels).filter_by(id=channel_id).first()
        return res


def get_scheduled_stream(stream_id):
    with session_scope() as session:
        res = session.query(AnnouncedStreams).filter_by(id=stream_id).first()
        return res


def add_scheduled_stream(channel_id, stream_id, scheduled_date):
    with session_scope() as session:
        if not get_scheduled_stream(stream_id):
            new_announced_stream = AnnouncedStreams(
                id=stream_id,
                channel_id=channel_id,
                scheduled_date=scheduled_date
            )
            session.add(new_announced_stream)


def delete_scheduled_stream(stream_id):
    with session_scope() as session:
        if get_scheduled_stream(stream_id):
            session.query(AnnouncedStreams).filter_by(id=stream_id).delete()


def get_started_stream(stream_id):
    with session_scope() as session:
        res = session.query(CurrentStreams).filter_by(id=stream_id).first()
        return res


def add_started_stream(channel_id, stream_id, start_date, scheduled):
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
    with session_scope() as session:
        if get_started_stream(stream_id):
            session.query(CurrentStreams).filter_by(id=stream_id).delete()


def get_finished_stream(stream_id):
    with session_scope() as session:
        res = session.query(FinishedStreams).filter_by(id=stream_id).first()
        return res


def add_finished_stream(channel_id, stream_id, start_date, end_date, duration, watchers, scheduled):
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


def add_stream_viewers(stream_id):
    key = 'stream:{}'.format(stream_id)
    if not redis_con.hgetall(key):
        value = {
            'current_viewers': 0,
            'max_viewers': 0
        }
        redis_con.hmset(key, value)


def update_viewers_count(stream_id, incr_val):
    key = 'stream:{}'.format(stream_id)
    if redis_con.hgetall(key):
        redis_con.incrby(key, 'current_viewers', incr_val)
        current_viewers = redis_con.hget(key, 'current_viewers')
        max_viewers = redis_con.hget(key, 'max_viewers')
        if current_viewers > max_viewers:
            redis_con.hset(key, 'max_viewers', current_viewers)


def get_max_viewers_count(stream_id):
    key = 'stream:{}'.format(stream_id)
    if redis_con.hgetall(key):
        return redis_con.hget(key, 'max_viewers')


def delete_stream_viewers(stream_id):
    key = 'stream:{}'.format(stream_id)
    if redis_con.hgetall(key):
        redis_con.delete(key)


async def handler(update):
    channel_id = None
    # Если прилетел интересующий нас ивент
    if isinstance(update, UpdateGroupCall) or isinstance(update, UpdateGroupCallParticipants):
        update = update.to_dict()
        # print(update)

        call = update.get('call')
        stream_id = str(call.get('id'))
        if update.get('chat_id'):
            channel_id = str(update.get('chat_id'))
            if not get_channel_info(channel_id):
                name, username, subscribers = await tg_channel_data(int(channel_id))
                if not subscribers:
                    subscribers = 0
                add_channel_info(channel_id, name, username, subscribers, None)

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
                    duration = call.get('duration')
                    # watchers_count = ???
                    end_date = datetime.now(tz=from_zone)
                    started_stream = get_started_stream(stream_id)
                    delete_started_stream(stream_id)
                    add_finished_stream(
                        channel_id=channel_id,
                        stream_id=stream_id,
                        start_date=started_stream.start_date,
                        end_date=end_date,
                        duration=duration,
                        watchers=0,
                        scheduled=started_stream.scheduled
                    )

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

        # Обработка ивентов с участниками стрима
        elif update.get('_') == 'UpdateGroupCallParticipants':
            participant = 0


client.add_event_handler(handler)

client.start()
client.run_until_disconnected()
