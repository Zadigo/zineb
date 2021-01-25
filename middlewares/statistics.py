class GeneralStatistics:
    counter = 0

    def __call__(self, sender, **kwargs):
        print('GeneralStatistics', sender, kwargs)
        # self.increase_counter()

    def increase_counter(self):
        self.counter = self.counter + 1
