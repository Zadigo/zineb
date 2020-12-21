class UserAgent:
    def __call__(self, sender, signal, **kwargs):
        print(sender, signal, **kwargs)
