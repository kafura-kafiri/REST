from crud.views import keyword
from flask import Blueprint, request
from config import keywords
from tools.utility import request_attributes, obj2str
from pymongo import DESCENDING

_keywords = {}
_max_length = 2


def add_keyword(key):
    if key not in _keywords:
        _keywords[key] = 1
    else:
        _keywords[key] += 1
    if len(_keywords) == _max_length:
        for key, hit in _keywords.items():
            try:
                result = keywords.find_and_modify(
                    {"title": key},
                    {"$inc": { "hit": hit }},
                )
                if not result:
                    raise
            except:
                keywords.insert_one({
                    "title": key,
                    "hit": 1,
                })
        _keywords.clear()


@keyword.blue.route('/sug/')
def suggest_keywords(query, size):
    query = query if query else request_attributes(request, query=str)['query']
    size = size if size else request_attributes(request, size=int)['size']
    __keywords = keywords.find(
        {'$or':
            [
                {'$text': {'$search': query}},
                {'title': {'$regex': query}},
            ]
        }
    ).sort(
        'hit', DESCENDING
    ).limit(
        size
    )
    return __keywords