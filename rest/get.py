from flask import request, render_template, abort, jsonify
from tools.utility import request_json, str2obj, obj2str, dot_notation, free_from_
from flask_login import current_user
from bson import ObjectId
import datetime
from copy import deepcopy
import json
import demjson


def add_gettation(crud):
    @crud.blue.route('/<_id>-<dash>', methods=['GET', 'POST'])
    @crud.blue.route('/<_id>-', methods=['GET', 'POST'])
    def minimize(_id, dash=''):
        fields = []
        if 'p' in dash and crud.projection:
            fields.append(crud.projection)
        try:
            document = crud.collection.find_one({'_id': ObjectId(_id)}, *fields)
            obj2str(document)
            return jsonify(document)
        except Exception as e:
            return str(e)

    @crud.blue.route('/-<dash>')
    @crud.blue.route('/-')
    @crud.blue.route('/{<_filter>}-<dash>')
    @crud.blue.route('/{<_filter>}-')
    def minimize_all(dash='', _filter='{}'):
        fields = []
        _filter = demjson.decode(_filter)
        _filter = str2obj(_filter)
        if 'p' in dash and crud.projection:
            fields.append(crud.projection)
        documents = crud.collection.find(_filter, *fields)
        documents = [obj2str(document) for document in documents]
        return jsonify(documents)

    @crud.blue.route('/<_id>')
    def get(_id):
        try:
            document = crud.collection.find_one({'_id': ObjectId(_id)})
            document, ctx = crud.load_document(document)
        except Exception as e:
            return str(e), 403
        return crud.render_template(crud.template_folder + '.html', **document, **ctx)

