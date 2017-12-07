from flask import Blueprint, render_template
from config import reviews, hows, products, pr
from crud import crud
from crud.review.instance import review
from bson import ObjectId
import importlib
blue = Blueprint('reviews', __name__, template_folder='templates')


def update_structure(r):
    _reviews = reviews.find({'_id': {'$in': r['reviews']}})
    _r = init_structure()
    _r['reviews'] = r['reviews']
    for _review in _reviews:
        _r['score']['population'][str(_review['score'])] += 1
        _r['score']['population']['total'] += 1
    s = 0
    for i in range(1, 6):
        s += i * _r['score']['population'][str(i)]
    _r['score']['value'] = s / _r['score']['population']['total']
    return _r


def on_delete_redundancy(_review):
    collection = _review['coolie']['type']
    collection = globals()[collection]
    document = _review['coolie']['_id']
    document = collection.find_one({'_id': document})
    document['reviews']['reviews'].remove(_review['_id'])
    document['reviews'] = update_structure(document['reviews'])
    collection.save(document)


def on_insert_redundancy(_review):
    collection = _review['coolie']['type']
    collection = globals()[collection]
    document = _review['coolie']['_id']
    document = collection.find_one({'_id': document})
    document['reviews']['reviews'].append(_review['_id'])
    print('rev rev')
    print(document['reviews']['reviews'])
    document['reviews'] = update_structure(document['reviews'])
    collection.save(document)
    print('rev rev')
    print(document['reviews']['reviews'])


def on_update_redundancy(_review):
    collection = _review['coolie']['type']
    collection = globals()[collection]
    document = _review['coolie']['_id']
    document = collection.find_one({'_id': document})
    document['reviews'] = update_structure(document['reviews'])
    collection.save(document)


crud(blue, reviews, skeleton=review, template='review', redundancies={
    'update': on_update_redundancy,
    'insert': on_insert_redundancy,
    'delete': on_delete_redundancy
})


def bring_reviews(document, limit=5, skip=0):
    _reviews = document['reviews']['reviews']
    _reviews = _reviews[skip:skip + limit]
    _top_review = document['reviews']['top_review']
    document['reviews']['reviews'] = reviews.find({'_id': {'$in': _reviews}})
    document['reviews']['top_review'] = reviews.find_one({'_id': _top_review})
    return document


def init_structure():
    return {
        'score': {
            'value': 5,
            'population': {
                'total': 1,
                '1': 0,
                '2': 0,
                '3': 0,
                '4': 0,
                '5': 1,
            },
        },
        'reviews': [],
        'top_review': '',
    }


@blue.route('/<collection>/<_id>/')
@blue.route('/<collection>/<_id>/<int:page_size>')
@blue.route('/<collection>/<_id>/<int:page_size>/<int:page>')
def full_review(collection, _id, page_size=10, page=1):
    skip = (page - 1) * page_size
    document = globals()[collection].find_one({'_id': ObjectId(_id)})
    document = bring_reviews(document, page_size, skip)
    return render_template('review/full_reviews.html', document=document, query={
        'page': page,
        'page_size': page_size,
        'collection': collection,
        '_id': _id,
    })