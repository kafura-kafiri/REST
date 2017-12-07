from flask import request, render_template, abort
from tools.utility import request_json, str2obj, obj2str, dot_notation, free_from_
from flask_login import current_user
from bson import ObjectId
import datetime
from copy import deepcopy
import json


def add_universal_alteration(crud):
    @crud.blue.route('/<_id>$$', methods=['GET', 'POST'])
    def universal_alter(_id):
        _id = ObjectId(_id)
        try:
            from pymongo import ReturnDocument
            _json = request_json(request)
            _json = free_from_(_json)
            _json = str2obj(_json)
            document = crud.collection.find_one_and_update(
                {'_id': _id},
                {'$set': _json},
                return_document=ReturnDocument.AFTER
            )
            crud._on_alter(document)
            document = obj2str(document)
            return render_template('crud/$$.html', **document)
        except Exception as e:
            print("sorry I can't update let's bring some thing to show")
            try:
                document = crud.collection.find_one({'_id': _id})
                if not document:
                    raise
                document = obj2str(document)
            except Exception as e:
                print("sorry I can't show any thing sorry for you")
                abort(404)
            return render_template('crud/$$.html', ctx=document)