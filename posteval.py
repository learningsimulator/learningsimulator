import ast
import re

from util import ParseUtil
from exceptions import EvalException


class PostVar():
    '''
    A variable to postprocessing functions such as v(s1->s2).
    '''
    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg
        self.parsed_arg = None  # self.arg parsed in parsing.py


class PostExpr():
    def __init__(self, expr, post_vars):
        self.expr = expr
        self.post_vars = post_vars  # dict

    def eval(self, simulation_data, parameters, run_parameters, variables, POST_MATH):
        # Evaluate each variable v(s->b), w(s), n(s->b->s)
        var_ydata = dict()  # Dict with evaluated ydata for each PostVar, keyed by alias variable
        n_values = None

        for alias, var in self.post_vars.items():
            var_ydata[alias] = simulation_data.vwpn_eval(var.fn, var.parsed_arg, parameters, run_parameters)
            if n_values is None:
                n_values = len(var_ydata[alias])
            else:  # Number of evaluated values should be the same for all variables
                assert(n_values == len(var_ydata[alias])), f"{n_values} != {len(var_ydata[alias])}"

        # Evaluate the expression using the evaluated variable values
        ydata = [None] * n_values
        for i in range(n_values):
            alias_values = {key: val[i] for key, val in var_ydata.items()}
            alias_values.update(POST_MATH)
            alias_values.update(variables.values)
            try:
                ydata[i] = eval(self.expr, {'__builtins__': {'round': round}}, alias_values)
            except Exception as e:
                # return None, raise EvalException(f"Expression evaluation failed.", self.lineno)
                return None, f"Expression evaluation failed."
        return ydata, None


def is_arithmetic(expr, allowed_names):
    """
    Checks that the specified expression is a valid post expression in the sense that its
    syntax is correct, and it contains only constants, specifed variables, binary
    operators (+, -, *, /, **) and math functions used in evaluation.
    """
    tree, err = ParseUtil.ast_parse(expr, include_expr_in_errmsg=False)
    if err is not None:  # Syntax error
        return False, err
    
    allowed_nodes = [ast.Expression, ast.Call, ast.Load,
                     ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
                     ast.UnaryOp, ast.USub]
    if hasattr(ast, 'Num'):  # Deprecated since Python 3.8
        allowed_nodes.append(ast.Num)
    if hasattr(ast, 'Constant'):  # Introduced in Python 3.8
        allowed_nodes.append(ast.Constant)

    for node in ast.walk(tree):
        if type(node) is ast.Name:
            if node.id not in allowed_names:
                return False, f"Invalid name {node.id} in expression."
        elif type(node) not in allowed_nodes:
            return False, f"Invalid expression."

    return True, None


def parse_postexpr(expr, variables, POST_MATH):
    '''
    Parse an expression to postprocessing functions such as
    "v(s1->b1) + v(s2->b2) - p(s2->b2) / 42 * sin(n(s1->b1->s2)) * w(s)"
    and returns the corresponding PostExpr object.
    '''
    def string_ind_replace(string, ind1, ind2, replacement):
        return string[:ind1] + replacement + string[ind2 + 1:]

    def make_alias_prefix(expr, variables):
        candidate = "_A"
        while (candidate in expr) or (variables.contains(candidate)):
            candidate = "_" + candidate
        return candidate

    ALIAS_PREFIX = make_alias_prefix(expr, variables)

    post_vars = dict()
    alias_expr = expr
    alias_cnt = 1
    for fn in ['v', 'p', 'w', 'vss', 'n']:
        fn_done = False
        while not fn_done:
            inds0 = [m.start() for m in re.finditer(fn + '[ \t]*[(]', alias_expr)]
            inds = []
            for ind in inds0:
                # For example sin(v(a->b)) should not catch "n("
                neglect = (ind > 0 and alias_expr[ind - 1].isalpha())
                if not neglect:
                    inds.append(ind)

            fn_done = (len(inds) == 0)
            if fn_done:
                break
            
            ind = inds[0]
            left_par_ind = ind + len(fn)
            right_par_ind = alias_expr[left_par_ind:].find(')')  # First ')' after 'fn('
            if right_par_ind == -1:
                return None, f"Missing right parenthesis in expression {expr}"
            right_par_ind += left_par_ind  # To get index to alias_expr, not alias_expr[left_par_ind:]
            arg = alias_expr[left_par_ind + 1: right_par_ind]
            alias = ALIAS_PREFIX + str(alias_cnt)
            alias_cnt += 1
            post_vars[alias] = PostVar(fn, arg)
            alias_expr = string_ind_replace(alias_expr, ind, right_par_ind, alias)
    
    if len(post_vars) == 0:  # Expression contains no v, p, w, n, or vss
        return None, f"Invalid expression {expr}"

    allowed_names = list(post_vars.keys()) + list(variables.values.keys()) + list(POST_MATH.keys()) + ['round']
    is_arithm, err = is_arithmetic(alias_expr, allowed_names)
    if not is_arithm:
        return None, err

    return PostExpr(alias_expr, post_vars), None
