dictionary = {}

def simplify(phrase):
    import string
    translator = str.maketrans('', '', string.punctuation)
    return phrase.translate(translator).lower().strip()

def digify(num):
    digits = {
        '0': '۰',
        '1': '۱',
        '2': '۲',
        '3': '۳',
        '4': '۴',

        '5': '۵',
        '6': '۶',
        '7': '۷',
        '8': '۸',
        '9': '۹',

        '.': '.',
    }
    num = str(num)
    _num = []
    for digit in num:
        _num.append(digits[digit])
    return ''.join(_num)


def translate(phrase, source='en', target='fa'):
    import requests
    import json
    _url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl={source}&tl={target}&dt=t&q={phrase}'\
        .format(source=source, target=target, phrase=phrase)
    r = requests.get(_url)
    r = r.content.decode('utf-8')
    r = json.loads(r)[0][0][0]
    return r


def trans(phrase):
    CSI = "\x1B[%sm"
    W = '\033[0m'  # white (normal)
    R = '\033[31m'  # red
    G = '\033[32m'  # green
    O = '\033[33m'  # orange
    B = '\033[34m'  # blue
    P = '\033[35m'  # purple
    if isinstance(phrase, str):
        phrase = phrase.rstrip()
        _phrase = phrase
        phrase = simplify(phrase)
        if phrase in dictionary:
            return dictionary[phrase]
        print((CSI % '5;30;41' + "'{}': '{}',".format(phrase, translate(_phrase)) + CSI % '0'))
        return phrase
    import numbers
    if isinstance(phrase, numbers.Real):
        return digify(phrase)
    else:
        return phrase


def update():
    _dic = {}
    for k, v in dictionary.items():
        _dic[simplify(k)] = v
    dictionary.clear()
    dictionary.update(_dic)
