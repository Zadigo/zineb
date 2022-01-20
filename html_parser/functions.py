from multiprocessing.sharedctypes import Value


class Function:
    query_attributes = {'eq', 'in', 'lt', 'gt', 
                        'contains', 'lte', 'gte', 'ne', 'none'}
    attributes = {'class', 'id', 'src', 'href'}
    
    def __init__(self, **expressions):
        self._extractor = None
        self._expressions = []
        self._expressions = self._resolve_expressions(expressions)
        
    @staticmethod
    def _comparision(comparator, a, b): 
        if b == True or b == False:
            return a == b
               
        if comparator == 'eq':
            return a == b
        
        if comparator == 'lt':
            return a < b
        
        if comparator == 'lte':
            return a <= b
        
        if comparator == 'gt':
            return a > b
        
        if comparator == 'gte':
            return a >= b
        
        if comparator == 'ne':
            return a != b
        
        if comparator == 'contains' or comparator == 'in':
            return a in b
        
        if comparator == 'none':
            return b is None
        
    def _resolve_expressions(self, expressions):
        authorized_values = self.query_attributes | self.attributes 
        for lh, rh in expressions.items():
            lh = lh.split('__')
            
            if len(lh) < 2:
                raise ValueError('Expression should contain at least two values which are the tag name and/or the attribute or query function')
            
            if lh[-1] not in authorized_values:
                raise ValueError('Expression does not contain a valid attribute')
            
            if len(lh) == 2:
                lh.append('eq')
            
            yield (lh, rh)
            
    def _do_comparision(self):
        if self._extractor is None:
            raise ValueError('Needs an extractor')
        
        for expression in self._expressions:
            tokens, value_to_compare = expression
            tag, attr, comparator = tokens
            
            for item in self._extractor:
                attr_value = item.get_attr(attr)
                if tag == item:
                    if self._comparision(comparator, value_to_compare, attr_value):
                        yield item


class Q(Function):
    """A helper function used to run more
    complex queries on the html page"""
    


q = Q(a__class__eq='Kendall', a__id='name', a__id__in=['a', 'b'])
print(list(q._expressions))
