from flask import request, render_template
from tools.utility import request_json, str2obj, obj2str, dot_notation
from flask_login import current_user
from bson import ObjectId
import datetime
from copy import deepcopy


def add_insertion(crud):
    @crud.blue.route('/+', methods=['GET', 'POST'])
    @crud.blue.route('/<_id>+', methods=['GET', 'POST'])
    def create(_id=None):
        if request.method == 'GET':
            return render_template(crud.singular_form + '/+.html')
        if request.method == 'POST':
            document = {}
            document = deepcopy(crud.default)
            try:
                _json = request_json(request)
                for key, value in _json.items():
                    sub_document, key = dot_notation(document, key)
                    sub_document[key] = value
            except:
                pass
            if _id:
                document['_id'] = ObjectId(_id)
            if current_user.is_authenticated:
                document['_author'] = current_user._id
            document['_date'] = datetime.datetime.now()

            result = crud.collection.insert_one(str2obj(document))
            crud._on_insert(document)

            return obj2str(result.inserted_id)