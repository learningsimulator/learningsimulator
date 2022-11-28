import ast
import re

from util import ParseUtil


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


def parse_postexpr_wont_work_with_compound_stimuli(expr0):
    '''
    Parse an expression to postprocessing functions such as
    "v(s1->b1) + v(s2->b2) - p(s2->b2) / 42 * sin(n(s1->b1->s2)) * w(s)"
    and returns the corresponding PostExpr object.

    First, replace -> with comma:
    v(s1,b1) + v(s2,b2) - p(s2,b2) / 42 * sin(n(s1,b1,s2)) * w(s)
    
    Then, remove all arguments to each function call v,p,w,vss,n but store the arguments in
    PostVar objects:
    v() + v() - p() / 42 * sin(n()) * w()

    Then, replace each empty function call with alias variable:
    S1 + S2 - S3 / 42 * sin(S4) * S5

    Store this expression and the created PostVar objects in the returned PostExpr object.
    '''
    # Replace -> with comma so that v(s->b) is interpreted as a function call v(s, b)
    expr = expr0.replace('->', ',')

    tree, err = ParseUtil.ast_parse(expr)
    if err is not None:
        return None, err

    # print(ast.dump(tree, indent=4))

    post_vars = dict()
    alias_cnt = 0
    replace_after_walk = dict()
    for node in ast.walk(tree):
        if type(node) is ast.Call and node.func.id in ('v', 'p', 'w', 'vss', 'n'):
            fn = node.func.id
            args = node.args
            if len(args) == 0:  # E.g. v()
                return None, f"No argument to {fn} given."
            args_list = [a.id for a in args]
            while len(args):  # Remove all arguments: v() + v() - p() / 42 * sin(n()) * w()
                args.pop()
            args_str = '->'.join(args_list)
            alias = '__S' + str(alias_cnt)
            alias_cnt += 1
            post_vars[alias] = PostVar(fn, args_str)
            replace_after_walk[fn + '()'] = alias  # After this loop, replace 
    
    # If (for some strange reason) any of "__S1()", "__S2()", etc. were already
    # present in the original expression, give error
    for orig in replace_after_walk:
        if orig in expr0:
            return None, f"Invalid part of expression: {orig}"

    alias_expr = ast.unparse(tree)
    for orig, replace_with in replace_after_walk.items():
        alias_expr = alias_expr.replace(orig, replace_with)

    return PostExpr(alias_expr, post_vars), None


def is_arithmetic(expr, allowed_names):
    """
    Checks that the specified expression is a valid post expression in the sense that its
    syntax is correct, and it contains only constants, specifed variables, binary
    operators (+, -, *, /, **) and math functions used in evaluation.
    """
    tree, err = ParseUtil.ast_parse(expr, include_expr_in_errmsg=False)
    if err is not None:  # Syntax error
        return False, err
    
    for node in ast.walk(tree):
        if type(node) is ast.Name:
            if node.id not in allowed_names:
                return False, f"Invalid name {node.id} in expression."
        elif type(node) not in (ast.Expression, ast.Call, ast.Constant, ast.Load,
                                ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
                                ast.UnaryOp, ast.USub):
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
            inds0 = [m.start() for m in re.finditer(fn + '[\s]*\(', alias_expr)]
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
