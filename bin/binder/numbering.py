
class Numbering:
    def __init__(self, indexes):
        self.indexes = indexes

    def get_index(self, s):
        stack = s.split('.')
        retour = []
        inx = self.indexes
        while len(stack) > 0:
            inx = inx[stack.pop(0)]
            if (inx.get('index', 0) == 0): break # We assume 0 is not to be included
            retour.append(str(inx.get('index', 0)))
        #print(str, retour)
        return '.'.join(retour)

    def reset(self, str, inx=None):
        if not inx:
            inx = self.indexes
        stack = str.split('.')
        for item in stack:
            inx = inx[item]

        inx['index'] = 0
        # Resetting sub_index
        for k, v in inx.items():
            if k != 'index':
                self.reset(k, inx)

    def bump(self, str):
        inx = self.indexes
        stack = str.split('.')
        for item in stack:
            inx = inx[item]

        inx['index'] = inx.get('index', 0) + 1
        # Resetting sub_index
        for k, v in inx.items():
            if k != 'index':
                self.reset(k, inx)

        return self.get_index(str)