class Index:
    NUMERAL = 'numeral'
    UPPERCASE = 'uppercase'

    def __init__(self, indexes=None, format='numeral'):
        self.format = format
        self.indexes = indexes or {}
        self.indice = None

    def next_index(self):
        if self.format == self.UPPERCASE:
            if self.indice is None: return 'A'
            return str(chr(ord(self.indice) + 1))
        if self.format == self.NUMERAL:
            if self.indice is None: return '1'
            return str(int(self.indice) + 1)
        return '0' # Default is numeral

    def change_format(self, new_format):
        self.format = new_format
        self.reset()

    def reset(self):
        """ Reset index to first value """
        self.indice = None
        for index in self.indexes.values():
            index.reset()
        
    def get(self, s):
        """ Return an Index or a sub index based on a string chained by dot. """
        stack = s.split('.')
        index_name = stack.pop(0)
        if index_name == '': return self
        return self.indexes.get(index_name).get('.'.join(stack))
    
    def bump(self):
        """ Bump index to the next value """
        self.indice = self.next_index()
        for index in self.indexes.values():
            index.reset()
            
    def value(self, s):
        stack = s.split('.')
        index_name = stack.pop(0)
        sub_index = self.indexes.get(index_name)
        if not sub_index: return ''
        sub_index_value = sub_index.value('.'.join(stack))
        if sub_index_value:
            if sub_index.indice:
                return sub_index.indice + '.' + sub_index_value
        return sub_index.indice
