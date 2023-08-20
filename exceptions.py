class ParseException(Exception):
    def __init__(self, lineno, msg):
        if lineno is not None:
            super().__init__("Error on line {}".format(lineno) + ": " + msg)
        else:
            super().__init__("Error: " + msg)
        self.lineno = lineno


class EvalException(Exception):
    def __init__(self, msg, lineno=None):
        if lineno is None:
            super().__init__(msg)
        else:
            super().__init__("Error on line {}".format(lineno) + ": " + msg)


class InterruptedSimulation(Exception):
    def __init__(self):
        super().__init__()

# class GuiException(Exception):
#     def __init__(self, code, msg):
#         super().__init__(code, msg)
