class T:
    contents = []
    name = ''

    def __str__(self):
        return ''.join(self.get_representation)

    @property
    def get_representation(self):
        representation = [str(tag) for tag in self.contents]
        representation.insert(0, f"<{self.name}>")
        representation.append(f"</{self.name}>")
        return representation


class A(T):
    contents = ['<h1></h1>']
    name = 'div'


class B(T):
    contents = [A()]
    name = 'span'


i = B()
print(i)
