class SpiderOptions(dict):
    spider_options = defaultdict(set)

    def __init__(self, **kwargs):
        self.errors = []

    @staticmethod
    def _check_value_against(value: Any):
        def checker(constraint, message: str):
            if not isinstance(value, constraint):
                raise ValueError(message)
        return checker

    def _checks(self):
        return [
            ('domains', self._check_domains),
            ('base_url', self._check_value_against),
            ('verbose_name', self._check_value_against),
            ('sorting', self._check_sorting),
            ('limit_request_to', self._check_value_against)
        ]

    def _precheck_options(self, options: dict):
        allowed_options = ['domains', 'base_url', 'verbose_name', 'sorting', 'limit_requests_to']
        for key, value in options.items():
            if key not in allowed_options:
                self.errors.append(key)
            else:
                # if key == 'domains':
                #     self._check_domains(value)
                
                # if key == 'base_url':
                #     if not value.startswith('http') or not value.startswith('https'):
                #         raise ValueError('Base url should start with http:// or https://')

                # if key == 'verbose_name':
                #     if not isinstance(value, str):
                #         raise ValueError('Base url should be a string')

                # if key == 'sorting':
                #     self._check_sorting(value)

                # if key == 'limit_requests_to':
                #     self

                for check in self._checks():
                    name, func = check
                    if name == key:
                        if func.__name__ == '_check_value_against':
                            checker = func(value)
                            checker()
                
                self.spider_options.setdefault(key, value)

        if self.errors:
            raise KeyError((f"{self.__class__.__name__} received "
            f"invalid options: {', '.join(self.errors)}"))

    def _check_domains(self, domains):
        if not isinstance(domains, (list, tuple)):
            raise TypeError('Domains should be either a tuple or an array')

        for url in domains:
            if url.startswith('http') or url.startswith('https'):
                raise ValueError('Domain should not start with http:// or http:s//')

    def _check_sorting(self, values):
        self._check_value_against(values, (list, tuple),'Sorting should be a list or a tuple')
        for value in values:
            self._check_value_against(value, str, 'Sorting parameter should be a string')
        
    def _check_url_domain(self, url: str) -> bool:
        restricted_domains = self.spider_options.get('domains')
        return url in restricted_domains

    def get(self, key: str):
        return self.spider_options[key]

    def setdefault(self, key: str, value: str):
        return self.spider_options.setdefault(key, value)
