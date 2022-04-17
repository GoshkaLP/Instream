from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Channels(Base):
    __tablename__ = 'channels'
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    name = Column(String, nullable=False)
    photo = Column(BYTEA)
    subscribers = Column(Integer, nullable=False)


class AnnouncedStreams(Base):
    __tablename__ = 'announcedstreams'
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, nullable=False)
    channel_id = Column(String, ForeignKey('channels.id'), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)


class CurrentStreams(Base):
    __tablename__ = 'currentstreams'
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, nullable=False)
    channel_id = Column(String, ForeignKey('channels.id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    scheduled = Column(Boolean, default=False)


class FinishedStreams(Base):
    __tablename__ = 'finishedstreams'
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, nullable=False)
    channel_id = Column(String, ForeignKey('channels.id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    viewers_count = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    scheduled = Column(Boolean, default=False)


class SuggestedChannels(Base):
    __tablename__ = 'suggestedchannels'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    information = Column(String)
    status = Column(Boolean, default=False)


class Bugs(Base):
    __tablename__ = 'bugs'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    information = Column(String, nullable=False)
    status = Column(Boolean, default=False)
