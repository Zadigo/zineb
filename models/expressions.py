from typing import Tuple, Union
from bs4.element import Tag
from itertools import chain
from bs4 import BeautifulSoup


class Expression:
    soup = None

    def __init__(self, tag: str, attrs: dict={}):
        self.tag = tag
        self.attrs = attrs
        self.elements = []

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    @staticmethod
    def parse_condition(expression: str):
        if '=' not in expression:
            raise ValueError('Should be an expression')
        return expression.split('=', maxsplit=1)

    def resolve(self, soup: BeautifulSoup):
        self.soup = soup
        self.elements = soup.find_all(self.tag, attrs=self.attrs)


class IfThen(Expression):
    def __init__(self, tag: str, if_condition: str, then_condition: str, attrs: dict={}):
        super().__init__(tag, attrs)
        self.if_condition = if_condition
        self.then_condition = then_condition

    def resolve(self, soup: BeautifulSoup):
        super().resolve(soup)
        attr, attr_value = self.parse_condition(self.if_condition)

        def logic(element: Tag):
            attr_exists = element.has_attr(attr)
            if attr_exists:
                if element.attrs[attr] == attr_value:
                    return True
            return False

        filtered_elements = filter(logic, self.elements)

        def implement_then(element: Tag):
            element.attrs[attr] = self.then_condition
            return element

        return map(implement_then, filtered_elements)


class And(Expression):
    def __init__(self, tag: str, *expressions):
        super().__init__(tag)

        self.expressions = [
            self.parse_condition(expression) 
                for expression in expressions
        ]

    def resolve(self, soup: BeautifulSoup):
        super().resolve(soup)

        filtered_elements = []

        for element in self.elements:
            truth_array = []
            for expression in self.expressions:
                attr, attr_value = expression
                attr_exists = element.has_attr(attr)
                if attr_exists:
                    if element.attrs[attr] == attr_value:
                        truth_array.append(True)
                    else:
                        truth_array.append(False)
                else:
                    truth_array.append(False)
            result = all(truth_array)
            if result:
                filtered_elements.append(element)
        return filtered_elements


class Or(Expression):
    def __init__(self, tag: str, *expressions):
        super().__init__(tag)

        self.expressions = [
            self.parse_condition(expression)
            for expression in expressions
        ]

    def resolve(self, soup: BeautifulSoup):
        super().resolve(soup)

        filtered_elements = []

        for element in self.elements:
            truth_array = []
            for expression in self.expressions:
                attr, attr_value = expression
                attr_exists = element.has_attr(attr)
                if attr_exists:
                    if element.attrs[attr] == attr_value:
                        truth_array.append(True)
                    else:
                        truth_array.append(False)
                else:
                    truth_array.append(False)
            result = any(truth_array)
            if result:
                filtered_elements.append(element)
        return filtered_elements


class Q(Expression):
    def __init__(self, tag: str, attrs: dict={}):
        pass


class Conditions:
    def __init__(self, soup: BeautifulSoup, *conditions: Tuple[Union[IfThen, Or, And, Q]]):
        self.conditions = list(conditions)
        results = [condition.resolve(soup) for condition in conditions]
        self.chained_results = chain(*results)

    def __repr__(self):
        return str(list(self.chained_results))
    
    def __getitem__(self, index):
        return list(self.chained_results)[index]

with open('tests/html/test_links.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')
    # a = Conditions(soup, IfThen('a', if_condition='id=title', then_condition='value2'))
    c = Conditions(soup, And('a', 'id=title', 'class=title'), Or('a', 'id=other'))
    print(c)
