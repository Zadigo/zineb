from utils.formatting import LazyFormat


class Rule:
    def __init__(self, request, **kwargs):
        self.is_success = self.run(**kwargs)

    def on_fail(self, **kwargs):
        return True

    def on_success(self, **kwargs):
        return True

    def run(self, **kwargs):
        funcs = [
            self.on_fail,
            self.on_success
        ]

        results = []
        for func in funcs:
            result = func(**kwargs)
            if not isinstance(result, bool):
                raise ValueError(LazyFormat('Rule function ({func}) should '
                'return a boolean'), func=func.__name__)
            results.append(result)
        return all(results)
