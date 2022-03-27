from app.views.extensions.models.models import Channels, AnnouncedStreams, CurrentStreams, FinishedStreams
from app.views.extensions.models.dbhelper import session_scope

from sqlalchemy import desc


def get_last_finished():
    """
    Метод для получения последних 5ти завершенных трансляций
    """
    with session_scope() as session:
        data = session.query(FinishedStreams, Channels).\
            filter(FinishedStreams.channel_id == Channels.id).\
            order_by(desc(FinishedStreams.end_date)).limit(5).all()
        resp_data = []
        for element in data:
            stream, channel = element[0], element[1]
            resp_data.append({
                'streamId': stream.id,
                'channelId': stream.channel_id,
                'channelUrl': 't.me/{}'.format(channel.username),
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
            stream, channel = element[0], element[1]
            resp_data.append({
                'streamId': stream.id,
                'channelId': stream.channel_id,
                'channelUrl': 't.me/{}'.format(channel.username),
                'scheduledDate': stream.scheduled_date
            })
        return {
            'announcedStreams': resp_data
        }


def get_current_streams():
    """
    Метод для получения текущих трансляций
    """
    with session_scope() as session:
        data = session.query(CurrentStreams, Channels).\
            filter(CurrentStreams.channel_id == Channels.id).all()
        resp_data = []
        for element in data:
            stream, channel = element[0], element[1]
            resp_data.append({
                'streamId': stream.id,
                'channelId': stream.channel_id,
                'channelUrl': 't.me/{}'.format(channel.username),
                'startDate': stream.start_date,
                'scheduled': stream.scheduled
            })
        return {
            'currentStreams': resp_data
        }