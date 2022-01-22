from zineb.html_parser.queryset import QuerySet


class Function:
    OPERATORS = {'eq': '=', 'in': '=', 'lt': '<', 'gt': '>', 'contains': '=', 
                 'lte': '<=', 'gte': '>=', 'ne': '!=', 'none': 'None'}
    query_attributes = {'eq', 'in', 'lt', 'gt', 
                        'contains', 'lte', 'gte', 'ne', 'none'}
    attributes = {'class', 'id', 'src', 'href'}
    
    def __init__(self, **expressions):
        self._extractor_instance = None
        self._expressions = []
        self._expressions = list(self._resolve_expressions(expressions))
        self._resolved_queryset = None
        # self._truth_arrays = []
        
    def __repr__(self):
        expressions = []
        for lhs, value_to_compare in self._expressions:
            tag, attr, operator = lhs
            expression = f"<{tag}{self.OPERATORS.get(operator)}{value_to_compare}>"
            expressions.append(expression)
        return f"{self.__class__.__name__}([{', '.join(expressions)}])"
        
    @staticmethod
    def _comparision(comparator, a, b):
        if a is None:
            return False
        
        if b is None:
            return False
        
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
            return b in a
        
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
        if self._extractor_instance is None:
            raise ValueError('Needs an extractor')
        
        for expression in self._expressions:
            tokens, value_to_compare = expression
            tag, attr, comparator = tokens
            
            for item in self._extractor_instance:
                attr_value = item.get_attr(attr)
                if tag == item.name:
                    if self._comparision(comparator, value_to_compare, attr_value):
                        yield item


class Combination:
    OPERATORS = {'and': 'AND', 'or': 'OR'}
    
    def __init__(self, initial_func, func_to_combine, operator='and'):
        self._extractor_instance = None
        self._operator = operator
        self._functions = [initial_func, func_to_combine]

        self.initial_func = initial_func
        self.func_to_combine = func_to_combine
        
        self._expressions = [
            self.initial_func._expressions[0], 
            self.OPERATORS[operator],
            self.func_to_combine._expressions[0]
        ]
        self._querysets = []
        
    def __repr__(self):
        reprs = [f"<{repr(self.initial_func)}>"]
        reprs.append(f"<{repr(self.func_to_combine)}>")
        return f"{self.__class__.__name__}({' '.join(reprs)})"
    
    def set_functions(self):
        # Make each sub function know about
        # the queryset in the Combination class
        # so that they can resolve their expressions
        # and store their own resolution of the queryset
        for func in self._functions:
            func._extractor_instance = self._extractor_instance
            self._querysets.append(func.resolve_query())

    def resolve_query(self):
        pass


class Q(Function):
    """A helper function used to run more
    complex queries on the html page"""

    def __and__(self, obj):
        return Combination(self, obj, operator='and')
    
    def __or__(self, obj):
        return Combination(self, obj, operator='or')
    
    def resolve_query(self):
        result = []
        for item in self._extractor_instance:
            thruth_array = []
            
            for expression in self._expressions:
                lhs, value_to_compare = expression
                tag, attr, operator = lhs
                if tag == item.name:
                    thruth_array.append(Function._comparision(operator, item[attr], value_to_compare))
                    
            if all(thruth_array):
                result.append(item)
        self._resolved_queryset = QuerySet.copy(result)
        return self._resolved_queryset


from zineb.html_parser.html_tags import Tag

tags = [Tag('a'), Tag('a', attrs=[('id', 'name')]), Tag('a', attrs=[('id', 'a')])]

# q = Q(a__id='a')
# q._extractor_instance = tags
# q.resolve_query()

q1 = Q(a__class__eq='Kendall')
q2 = Q(a__id='name')
q3 = Q(a__id='names', a__id__ne='star')
c = q1 | q2
c._extractor_instance = tags
c.set_functions()
print(c._functions)
