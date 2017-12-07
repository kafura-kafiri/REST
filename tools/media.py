# !/usr/bin/env python
# -*- coding: utf-8 -*-

from config import fs
import mimetypes
import requests
from io import BytesIO
from PIL import Image
from bson import ObjectId

from flask import send_file, Blueprint, request, flash, abort
blue = Blueprint('media', __name__)


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


def insert_img(image_bytes, o, sizes=('b', 't', 'k', 'r', 'v', 'w', 'y', 'l'), mime_type='image/jpeg'):
    import io
    dec = {
        'b': 50,
        't': 100,
        'k': 120,
        'r': 240,
        'w': 300,
        'v': 600,
        'y': 800,
        'l': 1600,
    }
    file_name = '{0}_{1}'.format('n', str(o))
    fs.put(image_bytes, contentType=mime_type, filename=file_name)
    for width, size in [(dec[size], size) for size in sizes]:
        img = Image.open(io.BytesIO(image_bytes))
        wpercent = (width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((width, hsize), Image.ANTIALIAS)
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='PNG')
        file_name = '{0}_{1}'.format(size, str(o))
        fs.put(imgByteArr.getvalue(), contentType=mime_type, filename=file_name)
    return str(o), 200


@blue.route('/+', methods=['GET', 'POST'])
def add_image():
    try:
        o = ObjectId()
        if 'url' in request.values:
            url = request.values['url']
            mime_type = mimetypes.guess_type(url)[0]
            r = requests.get(url, stream=True)
            return insert_img(r.raw.read(), o, mime_type=mime_type)
        if 'file' in request.files:
            file = request.files['file']
            mime_type = mimetypes.guess_type(file.filename)[0]
            return insert_img(file.read(), o, mime_type=mime_type)
        raise Exception
    except Exception as e:
        abort(400)


@blue.route('/-')
def minimize_all():
    from utility import obj2str
    from flask import jsonify
    documents = fs.find()
    documents = [{
            '_id': str(document._id),
            'filename': document.filename,
        } for document in documents]
    return jsonify(documents)


@blue.route('/*', methods=['GET', 'POST'])
#@login_required
def delete_all():
    import json
    for i in fs.find():
        fs.delete(i._id)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@blue.route('/<size>/<_id>.<_format>')
@blue.route('/<size>/<_id>')
def get_image(_id, size, _format=None):
    try:
        file_name = '{0}_{1}'.format(size, _id)
        im_stream = fs.get_last_version(filename=file_name)
        im = Image.open(im_stream)
        return serve_pil_image(im)
    except Exception as e:
        abort(400)
