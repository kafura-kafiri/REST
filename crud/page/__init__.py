from flask import Blueprint, request, jsonify, render_template
from config import pages
from crud import crud

skeleton = {
    'name': "",
    'html': '',
}

blue = Blueprint('page', __name__, template_folder='templates')
crud(blue, pages, template='page/index', skeleton=skeleton)


@blue.route('/the/<name>')
def symlink_get(name):
    page = pages.find_one({'name': name})
    return render_template('page/index.html', **page)