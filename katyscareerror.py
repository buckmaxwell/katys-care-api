class KatysCareError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class WrongUserError(KatysCareError):
    DEFAULT_VALUE = 'you cannot perform this action on a user other than yourself'

    def __init__(self, value=DEFAULT_VALUE):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Forbidden(KatysCareError):
    DEFAULT_VALUE = 'forbidden action'

    def __init__(self, value=DEFAULT_VALUE):
        self.value = value

    def __str__(self):
        return repr(self.value)