from flask import request, render_template
from tools.utility import request_json, str2obj, obj2str, dot_notation
from flask_login import current_user
from bson import ObjectId
import datetime
from copy import deepcopy
import json


def add_deletion(crud):
    @crud.blue.route('/*', methods=['GET', 'POST'])
    # @login_required
    def delete_all():
        crud.collection.delete_many({})
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    @crud.blue.route('/<_id>*', methods=['GET', 'POST'])
    # @login_required
    def delete(_id):
        document = crud.collection.find_one_and_delete({
            '_id': ObjectId(_id)
        })
        # document['_id'] = ObjectId(_id)
        crud._on_delete(document)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
