from pandas import DataFrame
from collections import deque
import pandas
from zineb.models.datastructure import Model


# class ResultContainer:
#     """
#     Allows the future combination of the results from multiple
#     models and help thus save one combined DataFrame
#     """
#     def __init__(self, model, callback=None):
#         self.model = model
#         self.callback = None

#     def __str__(self):
#         return str(self.model)

#     def __repr__(self):
#         return self.model

#     def __add__(self, model):
#         if not isinstance(model, DataFrame):
#             raise TypeError('Model should be a DataFrame object')
#         return pandas.concat([self.model, model], ignore_index=True)


class Pipe:
    def __init__(self, models, callbacks:list=[]):
        pseudo_dataframes = []
        for model in models:
           if isinstance(model, Model):
               pseudo_dataframes.append(model)
        self.pseudo_dataframes = pseudo_dataframes
        self.callbacks = callbacks

    def _resolve_dataframes(self):
        true_dataframes = []
        for model in self.pseudo_dataframes:
            true_dataframes.append(model.save(commit=False))
        return pandas.concat(true_dataframes, ignore_index=True)

    def _do_callbacks(self):
        unique_callbacks = set(self.callbacks)
        for callback in unique_callbacks:
            if callable(callback):
                callback(self._resolve_dataframes())
