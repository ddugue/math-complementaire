import unicodedata
import re
def next_or_none(iterator):
    try:
        return next(iterator)
    except StopIteration:
        return None

def pop_or_none(l):
    try:
        return l.pop(0)
    except IndexError:
        return None

def get_or_none(l, i):
    try:
        return l[i]
    except IndexError:
        return None

def slugify(value):
    value.replace('.', '-').replace(':','-')
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)