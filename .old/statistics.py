class GeneralStatistics:
    counter = 0

    def __call__(self, sender, method='increase', **kwargs):
        allowed_methods = {
            'increase': self.increase_counter,
            'decrease': self.decrease_counter,
            'save': self.save,
            'clear': self.clear
        }
        allowed_methods[method]()

    def increase_counter(self):
        self.counter = self.counter + 1

    def decrease_counter(self):
        self.counter = self.counter - 1
        
    def save(self):
        pass
    
    def clear(self):
        self.counter = 0
    