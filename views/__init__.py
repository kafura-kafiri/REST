from flask import Blueprint
blue = Blueprint('views', __name__,template_folder='templates')

import views.home
import views.search