from flask import render_template, request

from config import products, hows
from tools.utility import request_attributes, obj2str
from views import blue

from crud.keyword import add_keyword, suggest_keywords

import pymongo

@blue.route('/s/')
def result():
    _json = request_attributes(request, kw=str, category=str, brand=str, pagesize=int, page=int)
    add_keyword(_json['kw'])
    _products = []
    if 'onlyHows' not in request.values or request.values['onlyHows'] != 'on':
        _products = search(products, _json['kw'], _json['pagesize'], category=_json['category'], brand=_json['brand'], page=_json['page'], auto_completion=False)
        _products = [obj2str(_product) for _product in _products]
    _hows = search(hows, _json['kw'], 4, auto_completion=False)
    _hows = [obj2str(_h) for _h in _hows]
    ctx = {
        'lang': {
            'dimensions': {
                'currency': '$'
            }
        }
    }
    query = {
        'kw': _json['kw'],
        'category': _json['category'],
        'brand': _json['brand'],
        'page': _json['page'],
        'pagesize': _json['pagesize']
    }
    if 'onlyHows' in request.values and request.values['onlyHows'] == 'on':
        query['onlyHows'] = True
    return render_template('result/index.html', query=query, products=_products, hows=_hows, **ctx)


@blue.route('/sug/')
def suggest():
    kw = request_attributes(request, kw=str)['kw']
    _keywords = suggest_keywords(kw, 5)
    _keywords = [_keyword['title'] for _keyword in _keywords]

    _products = search(products, kw, 3)
    _products = [{
        'url': 'pr/' + str(_product['_id']),
        'dname': _product['title'],
        'img': str(_product['img'][0])
                 } for _product in _products]

    suggestion = {
        "products": _products,
        "general": _keywords,
    }
    import json
    suggestion = "iHerbSearchCompletion('{}');".format(json.dumps(suggestion, separators=(',', ':')))
    return suggestion