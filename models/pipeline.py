from typing import Type
from zineb.http.request import HTTPRequest
import pandas
from zineb.models.datastructure import Model


class Pipe:
    """
    A class used to combine the results of multiple
    models together

    Parameters
    ----------

            models (list): list of models to to combine
            callbacks (list, Optional): Defaults to []
    """
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
