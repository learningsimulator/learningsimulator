import keywords as kw
from util import ParseUtil, is_valid_name


class Variables():
    def __init__(self, values=None):
        if values:
            self.values = dict(values)
        else:
            self.values = dict()

    def add_cs_varvals(self, cs_varvals, pv):
        """
        Adds to self.values the variables and values in the specified comma-separated
        variable:value pairs ("var1:val1, var2:val2, ...").
        """
        err = "A @VARIABLES line should have the form '@VARIABLES var1:val1, var2:val2, ...'."
        varvals = ParseUtil.comma_split(cs_varvals)
        for varval in varvals:
            if varval.count(':') == 1 or varval.count('=') == 1:
                if varval.count('=') == 1:
                    sep = '='
                else:
                    sep = ':'
                var, val_str = varval.split(sep)
                var = var.strip()
                val_str = val_str.strip()
                if var not in self.values:  # Otherwise overwrite previous value
                    var_err = is_valid_name(var, pv, kw)
                    if var_err:
                        return var_err
                val, val_err = self._is_valid_value(val_str)
                if val_err:
                    return val_err
                else:
                    self.values[var] = val
            else:
                return err
        return None

    # XXX for ipython
    def add(self, name, value):
        self.values[name] = value

    def set(self, name, val, parameters):
        """
        Sets the specified value to the variable with the specified name. If there is no such
        variable in self.values, add a new, checking the variable name.

        Returns:
            The error message, if any. None otherwise.
        """
        if name not in self.values:
            err = is_valid_name(name, parameters, kw)
            if err:
                return err
        self.values[name] = val
        return None

    def contains(self, name):
        return name in self.values

    def is_empty(self):
        return not bool(self.values)

    def _is_valid_value(self, value_str):
        return ParseUtil.evaluate(value_str, self)
        # return ParseUtil.is_float(value_str)

    @staticmethod
    def join(variables1, variables2):
        joined_variables = Variables()
        joined_variables.values = {**variables1.values, **variables2.values}
        return joined_variables
