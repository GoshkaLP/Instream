from flask import Blueprint, request
from app.controllers.node_controller import get_last_finished, get_announced_streams, get_current_streams, \
    add_suggested_channel, add_bug, send_channel_photo


node = Blueprint('node', __name__)


@node.route('/api/status', methods=['GET'])
def api_version():
    return 'Server working!', 200


@node.route('/api/lastFinishedStreams', methods=['GET'])
def api_last_finished():
    return get_last_finished()


@node.route('/api/announcedStreams', methods=['GET'])
def api_announced_streams():
    return get_announced_streams()


@node.route('/api/currentStreams', methods=['GET'])
def api_current_streams():
    return get_current_streams()


@node.route('/api/suggestChannel', methods=['POST'])
def api_suggest_channel():
    return add_suggested_channel(request.json)


@node.route('/api/addBug', methods=['POST'])
def api_add_bug():
    return add_bug(request.json)


@node.route('/api/photo/<string:channel_id>', methods=['GET'])
def api_channel_photo(channel_id):
    return send_channel_photo(channel_id)
