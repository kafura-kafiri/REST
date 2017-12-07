from flask import Flask
app = Flask(__name__, template_folder='templates', static_folder='static')

from config import configure
configure(app)

from tools.media import blue as media
app.register_blueprint(media, url_prefix='/media')

from tools.backup import blue as backup
app.register_blueprint(backup, url_prefix='/backup')

from crud.views import register_all
register_all(app)

from views import blue as views
app.register_blueprint(views)

if __name__ == '__main__':
    app.run(port=5000)