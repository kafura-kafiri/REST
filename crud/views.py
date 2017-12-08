from rest import Crud


def register_all(app):
    for attr in globals().values():
        if isinstance(attr, Crud):
            app.register_blueprint(attr.blue, url_prefix='/' + attr.plural_form)

user = Crud('user', 'users')
user.crud()

keyword = Crud('keyword', 'keywords')
keyword.crud()

nephew = Crud('nephew', 'nephews')
nephew.crud()