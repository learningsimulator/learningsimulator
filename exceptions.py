class ParseException(Exception):
    def __init__(self, lineno, msg):
        if lineno is not None:
            super().__init__("Error on line {}".format(lineno) + ": " + msg)
        else:
            super().__init__("Error: " + msg)
        self.lineno = lineno
        self.msg = msg

    def __reduce__(self):
        return (self.__class__, (self.lineno, self.msg))


class EvalException(Exception):
    def __init__(self, msg, lineno=None):
        if lineno is None:
            super().__init__(msg)
        else:
            super().__init__("Error on line {}".format(lineno) + ": " + msg)
        self.lineno = lineno
        self.msg = msg

    def __reduce__(self):
        return (self.__class__, (self.msg, self.lineno))

class InterruptedSimulation(Exception):
    def __init__(self):
        super().__init__()

# class GuiException(Exception):
#     def __init__(self, code, msg):
#         super().__init__(code, msg)
