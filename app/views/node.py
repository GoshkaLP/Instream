from flask import Blueprint
from .node_logic import get_last_finished, get_announced_streams, get_current_streams


node = Blueprint('node', __name__)


@node.route('/api/status', methods=['GET'])
def api_version():
    return 'Server working!', 200


@node.route('/api/lastFinishedStreams', methods=['GET', 'POST'])
def api_last_finished():
    return get_last_finished()


@node.route('/api/announcedStreams', methods=['GET', 'POST'])
def api_announced_streams():
    return get_announced_streams()


@node.route('/api/currentStreams', methods=['GET', 'POST'])
def api_current_streams():
    return get_current_streams()
