import pip
import virtualenv

import sys
import os
import shutil
from distutils.dir_util import copy_tree

project_name = sys.argv[1]
project_parent_folder = sys.argv[2]

src = os.path.abspath('.')
dst = project_parent_folder + project_name


print('cloning')
copy_tree(src, dst)
print('done')
old_rest_script = os.path.join(dst, 'REST.py')
new_rest_script = os.path.join(dst, project_name + '.py')
os.rename(old_rest_script, new_rest_script)

print("deleting unnecessary files")
with open('.cloneignore') as f:
    for line in f.readlines():
        line = line.rstrip()
        if line[0] != '#':
            name = line
            if name[-1] == '/':
                shutil.rmtree(dst + '/' + name[:-1])
            else:
                os.remove(dst + '/' + name)


# create and activate the virtual environment
venv_dir = dst + '/' + '.venv'
virtualenv.create_environment(venv_dir)
activation_dir = os.path.join(venv_dir, "bin", "activate_this.py")
with open(activation_dir) as ac:
    exec(ac.read())

    # pip install a package using the venv as a prefix
    print("let's install packages")
    with open('requirements') as f:
        for line in f.readlines():
            package = line.strip()
            print(pip.main(["install", "--prefix", venv_dir, package]))
