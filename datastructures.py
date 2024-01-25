class Relation(frozenset):
    def __init__(self, *args, **kwargs):
        try:
            self.columns = frozenset(next(iter(self)).dictionary.keys())
        except:
            self.columns = frozenset()

    def __and__(self, other):
        return Relation(super().__and__(other))
    
    def __or__(self, other):
        return Relation(super().__or__(other))
    
    def __sub__(self, other):
        return Relation(super().__sub__(other))

class Row(frozenset):
    def __init__(self, *args, **kwargs):
        self.dictionary = dict(self)

    def __getitem__(self, key):
        return self.dictionary[key]
    
    def __and__(self, other):
        return Row(super().__and__(other))
    
    def __or__(self, other):
        return Row(super().__or__(other))
    
    def __sub__(self, other):
        return Row(super().__sub__(other))
