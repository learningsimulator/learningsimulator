import re

TIME_VALUE = 'time_value'
DATA_VALUE = 'data_value'


def to_bool(s):
    """Return True if the specified string is 'y' and False if it is None. Assertion False otherwise."""
    if s is None:
        return False
    elif s == 'y':
        return True
    else:
        assert(False), "Internal error."


def list_to_csv(x):
    """Create a comma-separated string representing the specified list."""
    if x is None:
        return ""
    x_quotes = list()
    for s in x:
        if s is not None:
            x_quotes.append('"' + s + '"')
        else:
            x_quotes.append('""')
    return ','.join(x_quotes)


def csv_to_list(csv_string):
    csv_list = csv_string.split(',')
    for i, s in enumerate(csv_list):
        csv_list[i] = csv_list[i].strip()

        # If string begins and ends with double-quote, remove thsee double-quotes
        if len(csv_list[i]) >= 2:
            first = csv_list[i][0]
            last = csv_list[i][-1]
            if (first == '"' and last == '"') or (first == "'" and last == "'"):
                csv_list[i] = csv_list[i][1:-1]
    return csv_list


def string_to_csv(string):
    # Split with respect to comma and newline
    l = re.split('\n|,', string)
    l = [x.strip() for x in l]

    return list_to_csv(l)
