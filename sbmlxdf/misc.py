"""Implementation of miscelanious functions.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import re

_map_mathml2numpy = (
# arithmetic operators
    ('abs', 'NP_NS.absolute'), ('exp', 'NP_NS.exp'), ('sqrt', 'NP_NS.sqrt'),
    ('sqr', 'NP_NS.square'), ('ln', 'NP_NS.log'), ('log10', 'NP_NS.log10'),
    ('floor', 'NP_NS.floor'), ('ceil', 'NP_NS.ceil'),
    ('factorial', 'NP_NS.math.factorial'), ('rem', 'NP_NS.fmod'),
# relational operators
    ('eq', 'NP_NS.equal'), ('neq', 'NP_NS.not_equal'), ('gt', 'NP_NS.greater'),
    ('lt', 'NP_NS.less'), ('geq', 'NP_NS.greater_equal'),
    ('leq', 'NP_NS.less_equal'),
# logical operators
    ('and', 'NP_NS.logical_and'), ('or', 'NP_NS.logical_or'),
    ('xor', 'NP_NS.logical_xor'), ('not', 'NP_NS.logical_not'),
    ('and', 'NP_NS.logical_and'), ('or', 'NP_NS.logical_or'),
    ('xor', 'NP_NS.logical_xor'), ('not', 'NP_NS.logical_not'),
# trigonometric operators
    ('sin', 'NP_NS.sin'), ('cos', 'NP_NS.cos'), ('tan', 'NP_NS.tan'),
    ('sec', '1.0/NP_NS.cos'), ('csc', '1.0/NP_NS.sin'),
    ('cot', '1.0/NP_NS.tan'),
    ('sinh', 'NP_NS.sinh'), ('cosh', 'NP_NS.cosh'), ('tanh', 'NP_NS.tanh'),
    ('sech', '1.0/NP_NS.cosh'), ('csch',' 1.0/NP_NS.sinh'),
    ('coth', '1.0/NP_NS.tanh'),
    ('asin', 'NP_NS.arcsin'), ('acos', 'NP_NS.arccos'),
    ('atan', 'NP_NS.arctan'), ('arcsinh', 'NP_NS.arcsinh'),
    ('arccosh', 'NP_NS.arccosh'), ('arctanh', 'NP_NS.arctanh'),
)

def mathml2numpy(mformula, np_ns='np'):
    """Convert mathml infix to a numpy formula.

    could be implemented as a (static) class
    """
    np_formula = ' ' + mformula
    np_formula = re.sub(r'\s?dimensionless\s?', ' ', np_formula)
    np_formula = re.sub(r'\^', '**', np_formula)
    np_formula = re.sub(r'\s?&&\s?', ' & ', np_formula)
    np_formula = re.sub(r'\s?\|\|\s?', ' | ', np_formula)
    for mathml_f, np_f in _map_mathml2numpy:
        np_formula = re.sub(r'\s+' + mathml_f + '\(',
                            ' ' + np_f.replace('NP_NS', np_ns) + '(',
                            np_formula)
    return np_formula.strip()


def extract_params(s):
    # extract parameters from a record and returns these in a dictionary
    # (key=value) are separated by ','
    # considers nested values in square brackets (key=[nested value])
    find_key = re.compile(r'\s*(?P<key>\w*)\s*=\s*')
    params = {}
    pos = 0
    while pos < len(s):
        m = find_key.search(s[pos:])
        if m:
            pos += m.end(0)
            if pos < len(s):
                if s[pos] == '[':
                    pos += 1
                    if pos >= len(s):
                        break
                    brackets = 1
                    for i in range(pos, len(s)):
                        if s[i] == ']':
                            brackets -= 1
                        if s[i] == '[':
                            brackets += 1
                        if brackets == 0:
                            break
                else:
                    for i in range(pos, len(s)):
                        if s[i] == ',':
                            break
                        if i == len(s)-1:
                            i += 1
                params[m['key']] = s[pos:i].strip()
                pos = i
        else:
            break
    return params


def extract_records(s):
    # extract records from a list of records
    # records are separated by ';'
    # considers nested values in square brackets (key=[nested values])
    records = []
    brackets = 0
    pos = 0
    while pos < len(s):
        for i in range(pos, len(s)):
            if s[i] == '[':
                brackets += 1
            if s[i] == ']':
                brackets -= 1
            if s[i] == ';' and brackets == 0:
                break
        if s[i] != ';':
            i += 1
        records.append(s[pos:i].strip())
        pos = i+1
    return records


def extract_lo_records(s):
    # extract list of records from a list of list of records
    # list of records are enclosed by square brackets and separated by ';'
    # "[record; record; ...];[record; record; ...]
    # considers nested values in square brackets (key=[nested values])
    lo_records = []
    pos = 0
    while pos < len(s):
        m = re.search('\[',s[pos:])
        if m:
            pos += m.end(0)
            brackets = 1
            if pos >= len(s):
                break
            for i in range(pos, len(s)):
                if s[i] == '[':
                    brackets += 1
                if s[i] == ']':
                    brackets -= 1
                if brackets == 0:
                    break
            if s[i] == ']':
                lo_records.append(s[pos:i].strip())
            pos = i+1
        else:
            break
    return lo_records
