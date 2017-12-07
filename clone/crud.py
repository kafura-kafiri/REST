import sys
import os
import errno


def create_file(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(filename, "w") as f:
        f.write("")


def append(filename, string):
    with open("test.txt", "a") as myfile:
        myfile.write(string)


def init_crud():
    child = sys.argv[2]
    child = child.lower()
    mother = "./crud"
    filename = os.path.join(mother, child, '__init__.py')
    create_file(filename)
    with open(filename, "a") as init_script:
        init_script.write('from crud.views import {name}'.format(name=child))
    filename = os.path.join(mother, child, 'templates', child, 'index.html')
    create_file(filename)
    filename = os.path.join(mother, child, 'templates', child, 'index_plus.html')
    create_file(filename)
    filename = os.path.join(mother, 'views.py')
    with open(filename, "a") as views_script:
        views_script.write("\n{name} = Crud('{name}', '{name}s')".format(name=child))
        views_script.write("\n{name}.crud()".format(name=child))
    filename = os.path.join(mother, 'defaults.py')
    with open(filename, "a") as default_script:
        default_script.write("\n{name} = {{}}".format(name=child))
        default_script.write("\n{name}_pr = {{}}".format(name=child))
    filename = 'config.py'
    with open(filename, "a") as config_script:
        config_script.write("\n{name}s = db['{upper_name}S']".format(name=child, upper_name=child.upper()))
        config_script.write("\n{name}s.drop_indexes()".format(name=child))