from app.models import Channels, AnnouncedStreams, CurrentStreams, FinishedStreams, \
    SuggestedChannels, Bugs

from db import session_scope, redis_con

from sqlalchemy import desc, func

from io import BytesIO

from flask import send_file

from os import getenv

from datetime import datetime

# Для отладки
# from dotenv import load_dotenv
# load_dotenv()


def get_last_finished():
    """
    Метод для получения завершенных трансляций в текущий день
    """
    current_date = datetime.utcnow().date()
    with session_scope() as session:
        data = session.query(FinishedStreams, Channels).\
            filter(FinishedStreams.channel_id == Channels.id,
                   func.date(FinishedStreams.end_date) == current_date).\
            order_by(desc(FinishedStreams.end_date)).all()
        resp_data = []
        for element in data:
            stream, channel = element
            resp_data.append({
                'streamId': stream.id,
                'channelId': stream.channel_id,
                'channelUrl': 'https://t.me/{}'.format(channel.username),
                'name': channel.username,
                'followersCount': channel.subscribers,
                'image': 'https://{}/api/photo/{}'.format(getenv('DOMAIN'), stream.channel_id),
                'startDate': stream.start_date,
                'endDate': stream.end_date,
                'viewersCount': stream.viewers_count,
                'duration': stream.duration,
                'scheduled': stream.scheduled
            })
        return {
            'finishedStreams': resp_data
        }


def get_announced_streams():
    """
    Метод для получения анонсированных трансляций
    """
    with session_scope() as session:
        data = session.query(AnnouncedStreams, Channels).\
            filter(AnnouncedStreams.channel_id == Channels.id).all()
        resp_data = []
        for element in data:
            stream, channel = element
            resp_data.append({
                'streamId': stream.id,
                'channelId': stream.channel_id,
                'channelUrl': 'https://t.me/{}'.format(channel.username),
                'name': channel.username,
                'followersCount': channel.subscribers,
                'image': 'https://{}/api/photo/{}'.format(getenv('DOMAIN'), stream.channel_id),
                'scheduledDate': stream.scheduled_date
            })
        return {
            'announcedStreams': resp_data
        }


def get_current_viewers(stream_id):
    """
    Метод для получения текущего числа зрителей начатого стрима из Redis
    """
    key = 'stream:{}'.format(stream_id)
    if redis_con.hgetall(key):
        return int(redis_con.hget(key, 'current_viewers'))


def get_current_streams():
    """
    Метод для получения текущих трансляций
    """
    with session_scope() as session:
        data = session.query(CurrentStreams, Channels).\
            filter(CurrentStreams.channel_id == Channels.id).all()
        resp_data = []
        for element in data:
            stream, channel = element
            resp_data.append({
                'streamId': stream.id,
                'channelId': stream.channel_id,
                'channelUrl': 'https://t.me/{}'.format(channel.username),
                'name': channel.username,
                'followersCount': channel.subscribers,
                'image': 'https://{}/api/photo/{}'.format(getenv('DOMAIN'), stream.channel_id),
                'startDate': stream.start_date,
                'scheduled': stream.scheduled,
                'viewersCount': get_current_viewers(stream.id)
            })
        return {
            'currentStreams': resp_data
        }


def add_suggested_channel(form):
    """
    Мето для добавления в базу предложенного канала
    """
    if form:
        username = form.get('username')
        information = form.get('information')
        if username:
            new_suggested_channel = SuggestedChannels(
                username=username,
                information=information
            )
            with session_scope() as session:
                session.add(new_suggested_channel)
            return {'status': 'ok'}
        return {'status': 'Empty required fields'}
    return {'status': 'Empty form'}


def add_bug(form):
    """
    Метод для добавления в базу информации о баге
    """
    if form:
        username = form.get('username')
        information = form.get('information')
        if username and information:
            new_bug = Bugs(
                username=username,
                information=information
            )
            with session_scope() as session:
                session.add(new_bug)
            return {'status': 'ok'}
        return {'status': 'Empty required fields'}
    return {'status': 'Empty form'}


def send_channel_photo(channel_id):
    """
    Метод для отправки фото запрашиваемого канала
    """
    with session_scope() as session:
        data = session.query(Channels).filter(Channels.id == channel_id).first()
        if data and data.photo:
            return send_file(
                BytesIO(data.photo),
                mimetype='image/jpeg',
                as_attachment=True,
                attachment_filename='photo.jpg')
    return {'status': 'No photo'}
