from bson import ObjectId
import demjson

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