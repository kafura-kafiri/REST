from bson import ObjectId
import demjson

import mimetypes
import os
import re

from flask import request, send_file, Response
def send_file_partial(path):
    """
        Simple wrapper around send_file which handles HTTP 206 Partial Content
        (byte ranges)
        TODO: handle all send_file args, mirror send_file's error handling
        (if it has any)
    """
    range_header = request.headers.get('Range', None)
    if not range_header: return send_file(path)

    size = os.path.getsize(path)
    byte1, byte2 = 0, None

    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()

    if g[0]: byte1 = int(g[0])
    if g[1]: byte2 = int(g[1])

    length = size - byte1
    if byte2 is not None:
        length = byte2 - byte1

    data = None
    with open(path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    rv = Response(data,
                  206,
                  mimetype=mimetypes.guess_type(path)[0],
                  direct_passthrough=True)
    rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))

    return rv

def my_send_file_partial(stream):
    range_header = request.headers.get('Range', None)
    if not range_header: return send_file(stream, mimetype=stream.content_type[0])

    size = stream.length
    byte1, byte2 = 0, None

    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()

    if g[0]: byte1 = int(g[0])
    if g[1]: byte2 = int(g[1])

    length = size - byte1
    if byte2 is not None:
        length = byte2 - byte1

    data = None
    stream.seek(byte1)
    data = stream.read(length)

    rv = Response(data,
                  206,
                  mimetype=stream.content_type[0],
                  direct_passthrough=True)
    rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))

    return rv


def request_json(request):
    '''
    :param request:
    :return:
    '''
    evaluated = {}
    try:
        evaluated = demjson.decode(request.values['json'], encoding='utf8')  # may # may not json
        for key, value in request.values.items():
            if 'json.' in key:
                key = '.'.join(key.split('.')[1:])
                evaluated, key = dot_notation(evaluated, key)
                try:
                    evaluated[key] = demjson.decode(value, encoding='utf8')
                except:
                    evaluated[key] = value
    finally:
        return evaluated


def request_attributes(request, **kwargs):
    values = request.values
    _json = {}
    for kay, _type in kwargs.items():
        if kay not in values:
            raise AttributeError()
        else:
            value = values[kay]
            if _type is str:
                evaluated_value = value
            else:
                evaluated_value = literal_eval(value)
                if type(evaluated_value) is not _type:
                    raise TypeError()
            _json[kay] = evaluated_value
    return _json


def obj2str(tree):
    if isinstance(tree, dict):
        for k, node in tree.items():
            tree[k] = obj2str(node)
        return tree
    elif isinstance(tree, list):
        _tree = []
        for node in tree:
            _tree.append(obj2str(node))
        return _tree
    elif isinstance(tree, ObjectId):
        return str(tree)
    else:
        return tree


def str2obj(tree):
    if isinstance(tree, dict):
        for k, node in tree.items():
            tree[k] = str2obj(node)
        return tree
    elif isinstance(tree, list):
        _tree = []
        for node in tree:
            _tree.append(str2obj(node))
        return _tree
    try:
        return ObjectId(tree)
    except:
        return tree


def free_from_(tree):
    if isinstance(tree, dict):
        new_tree = {}
        for k, node in tree.items():
            if '__' not in k:
                new_tree[k] = free_from_(node)
        return new_tree
    elif isinstance(tree, list):
        for idx, node in enumerate(tree):
            tree[idx] = free_from_(node)
    return tree


def dot_notation(_dict, key):
    keys = key.split('.')
    for key in keys[:-1]:
        if key not in _dict:
            _dict[key] = {}
        _dict = _dict[key]
    return _dict, keys[-1]