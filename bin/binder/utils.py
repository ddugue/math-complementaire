import unicodedata
import re
def next_or_none(iterator):
    "Returns the next item of the iterator or None if no more items"
    try:
        return next(iterator)
    except StopIteration:
        return None

def pop_or_none(l):
    "Pop the first item of the list or None if the list is empty"
    try:
        return l.pop(0)
    except IndexError:
        return None

def get_or_none(l, i):
    "Returns the item at index 'i' in the 'l' list or None if absent"
    try:
        return l[i]
    except IndexError:
        return None

def slugify(value):
    "Normalize a string by replacing spaces. Useful to make stuff url friendlys"
    #value.replace('.', '-').replace(':','-')
    value = value.replace('/','__')
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)