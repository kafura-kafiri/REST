import pymongo

def search(collection, kw, size, category=None, brand=None, page=1, auto_completion=True, _sort='relevance'):
    projection = {}
    search_selector = {
        "$or":
            [
                {"$text": {
                    "$search": kw,
                }},
            ],
    }
    if auto_completion:
        search_selector['$or'].append({'title': {'$regex': kw}})
    if kw == '' or not kw:
        del(search_selector['$or'])

    fields = {
        "$or": [
            {
                "categories": {
                    "$elemMatch": {"title": category}
                }
            }, {
                "categories": {
                    "$elemMatch": {
                        "ancestors": {
                            "$elemMatch": {"title": category}
                        }
                    }
                }
            }
        ],
        'brand.title': brand,
    }
    if category is None or category == '':
        del fields['$or']
    if brand is None or brand == '':
        del fields['brand.title']
    sort_by = {
        'relevance': (
            "score", {
                "$meta": "textScore"
            }
        ),
        'best selling': {},
        'costumer rating': ('reviews.score.value', pymongo.DESCENDING),
        'price low to high': ('value.our', pymongo.ASCENDING),
        'price high to low': ('value.our', pymongo.DESCENDING),
        'newest': ('_date', pymongo.DESCENDING),
        'heaviest': ('dimensions.weight.pure', pymongo.DESCENDING),
        'lightest': ('dimensions.weight.pure', pymongo.ASCENDING),
    }
    return collection.find(
        {
            **fields,
            **search_selector
        },
        {"score": {
            "$meta": "textScore"
        }},
    ).sort([sort_by[_sort]]).skip(
        size * (page - 1)
    ).limit(
        size
    )

