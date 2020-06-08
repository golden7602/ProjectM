class ShowClassName(object):
    def __init__(self, cls):
        self._cls = cls

    def __call__(self, a):
        print('class name:', self._cls.__name__)
        return self._cls(a)


@ShowClassName
class Foobar(object):
    def __init__(self, a):
        self.value = a

    def fun(self):
        print(self.value)


a = Foobar('xiemanR')

a.fun()