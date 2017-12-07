from bson import ObjectId
from flask import jsonify, render_template, abort, request, Blueprint
from flask_login import login_required, current_user
import json, demjson
from tools.utility import request_json, obj2str, free_from_, str2obj, dot_notation
import datetime
import importlib

from rest.insert import add_insertion
from rest.remove import add_deletion
from rest.universal_alter import add_universal_alteration
from rest.alter import add_alteration
from rest.get import add_gettation


class Crud:
    def __init__(self, singular_form, plural_form,

                 load_document=lambda x: (x, {}),

                 on_delete=lambda x: x,
                 on_insert=lambda x: x,
                 on_alter=lambda x: x,
                 ):
        self.singular_form = singular_form
        self.plural_form = plural_form
        self.blue = Blueprint(plural_form, __name__, template_folder=singular_form + '/templates/' + singular_form)
        self.collection = None
        self.default = {}
        self.projection = {}
        self._on_delete = on_delete
        self._on_insert = on_insert
        self._on_alter = on_alter
        self.load_document = load_document
        self.retrieve()

    #  switch on and off
    def login_required(self, boolean):
        self.blueprint = boolean

    def retrieve(self):
        config = importlib.import_module('config')
        self.collection = getattr(config, self.plural_form)
        defaults = importlib.import_module('crud.defaults')
        self.default = getattr(defaults, self.singular_form)
        self.projection = getattr(defaults, self.singular_form + '_pr')

    def crud(self):
        add_insertion(self)
        add_deletion(self)
        add_universal_alteration(self)
        add_alteration(self)
        add_gettation(self)
        importlib.import_module('crud.' + self.singular_form)
