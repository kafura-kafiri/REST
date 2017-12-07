from flask import Blueprint, request, jsonify, render_template, abort
from flask_login import current_user
from config import rooms
from crud import crud
from utility import request_attributes, obj2str
from bson import ObjectId
import datetime
import json
from services.tg import client
from config import users
import _thread
from telethon.tl.types import UpdateShortMessage, UpdateShortChatMessage, UpdateNewMessage
from ast import literal_eval

skeleton = {
    'messages': [],
    'members': [], #(ObjectId, seq_num)
}

message = {
    '_date': '',
    '_author': '',
    'text': '',
}

anonymous = '__anonymous__'

blue = Blueprint('room', __name__, template_folder='templates')
crud(blue, rooms, skeleton=skeleton)


def update_handler(update_object):
    '''if isinstance(update_object, UpdateShortMessage):
        print('You sent {} to user #{}'.format(update_object.message, update_object.user_id))
    if isinstance(update_object, UpdateShortChatMessage):
        print('You sent {} to chat #{}'.format(update_object.message, update_object.chat_id))'''
    if isinstance(update_object, UpdateNewMessage):
        if update_object.message.reply_to_msg_id:
            _text = update_object.message.message
            _message = client.get_message_history('+989133657623',  # this one is hard coded
                                                  min_id=update_object.message.reply_to_msg_id - 1,
                                                  max_id=update_object.message.reply_to_msg_id + 1)[1][0]
            ev = literal_eval(_message.message)
            _id = ev['_id']
            _author = ev['_author']
            send(_id, _text, _current_user={'_id': ObjectId(_author)})
client.add_update_handler(update_handler)


@blue.route('/<_id>/send/<text>')
def send(_id, text, _current_user=None):
    if not _current_user:
        author = current_user._id if current_user.is_authenticated else anonymous
    else:
        author = _current_user['_id']
    m = {
        '_date': datetime.datetime.now(),
        '_author': author,
        'text': text,
    }
    room = rooms.find_one({'_id': ObjectId(_id)})
    _members = room['members']
    if author in _members:
        _members = users.find({'_id': {'$in': _members}})
        for member in _members:
            if member['_id'] != author:
                if 'phone' in member:
                    _json = {
                        'text': '__text__',
                        '_id': _id,
                        '_author': str(member['_id'])
                    }
                    _json = json.dumps(_json)
                    print(_json)
                    _json = _json.replace('"text": "__text__"', '"text": "{}"'.format(text))
                    print(_json)
                    _thread.start_new_thread(client.send_message, (member['phone'], _json))
        room['messages'].append(m)
        rooms.save(room)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        abort(403)


@blue.route('/<_id>/receive/<int:seq_num>/<int:limit>')
@blue.route('/<_id>/receive/<int:limit>')
def receive(_id, limit, seq_num=None):
    if seq_num:
        head = seq_num
    else:
        head = -limit
    tail = head + limit
    room = rooms.find_one({'_id': ObjectId(_id)})
    messages = room['messages']
    if head < 0 and tail >= 0:
        _messages = messages[head:]
        tail = len(messages)
    else:
        _messages = messages[head:tail]
        if tail > len(messages):
            tail = len(messages)
        if tail < 0:
            tail += len(messages)
    _messages = [obj2str(message) for message in _messages]
    return jsonify({'messages': _messages, 'seq_num': tail})


@blue.route('/gram')
def gram():
    return render_template('room/instance.html')