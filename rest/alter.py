from flask import request, render_template, abort
from tools.utility import request_json, str2obj, obj2str, dot_notation, free_from_
from flask_login import current_user
from bson import ObjectId
import datetime
from copy import deepcopy
import json


def add_alteration(crud):
    @crud.blue.route('/<_id>$', methods=['GET', 'POST'])
    @crud.blue.route('/<_id>$-<operator>', methods=['GET', 'POST'])
    def alter(_id, operator):
        _id = ObjectId(_id)
        try:
            from pymongo import ReturnDocument
            if 'node' in request.values:
                _json = request_json(request, specific_type=None)
                node = request.values['node']
                if not _json:
                    document = crud.collection.find_one_and_update(
                        {'_id': _id},
                        {'$unset': {node: ""}},
                        return_document=ReturnDocument.AFTER
                    )
                else:
                    document = crud.collection.find_one_and_update(
                        {'_id': _id},
                        {'${}'.format(operator): {node: _json}},
                        return_document=ReturnDocument.AFTER
                    )
            else:
                _json = request_json(request)
                document = crud.collection.find_one_and_update(
                    {'_id': _id},
                    {'$set': _json},
                    return_document=ReturnDocument.AFTER
                )
            crud._on_alter(document)
            if 'ajax' in request.values:
                return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        except Exception as e:
            print(e)
            try:
                document = crud.collection.find_one({'_id': _id})
            except Exception as e:
                print(e)
                abort(405)
        document, ctx = crud.load_document(document)
        return render_template(crud.template_folder + '_plus.html', **document, **ctx)
