import sys
from clone.crud import init_crud
actions = {
    'crud': init_crud
}

actions[sys.argv[1]]()