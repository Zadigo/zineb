# class PositionMixin:
#     def __init__(self, field: str):
#         self.field_name = field

#     def get_field_cached_values(self):
#         return self.model._cached_result.get(self.field_name)


# class Last(PositionMixin, ExpressionMixin):
#     def resolve(self):
#         cached_values = self.get_field_cached_values()
#         return cached_values[-1]


# class First(PositionMixin, ExpressionMixin):
#     def resolve(self):
#         cached_values = self.get_field_cached_values()
#         result = cached_values[:1]
#         if result:
#             return result[-1]
#         return None


# class Latest:
#     pass


# class Earliest:
#     pass


# class Min(PositionMixin, ExpressionMixin):
#     def resolve(self):
#         cached_values = self.get_field_cached_values()
#         return min(cached_values)


# class Max(Min):
#     def resolve(self):
#         cached_values = self.get_field_cached_values()
#         return max(cached_values)


class F:
    """Maps all the values that were saved on
    a given model under a given field

    >>> F("name")
    ... [(1, "Kendall"), (2, "Kylie"), (3, "Aurélie")]
    """
    def __init__(self, name):
        self.model = None
        self.field = None
        self.field_name = name

    def map_values(self):
        pass


class Q:
    """Query values that were saved on a given
    model using an expression
    
    >>> Q(name__eq="Kendall")
    ... [(1, "Kendall")]
    """
