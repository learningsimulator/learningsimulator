class ParseException(Exception):
    def __init__(self, lineno, msg):
        super().__init__("Error on line {}".format(lineno) + ": " + msg)
        self.lineno = lineno


class EvalException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


# class GuiException(Exception):
#     def __init__(self, code, msg):
#         super().__init__(code, msg)
