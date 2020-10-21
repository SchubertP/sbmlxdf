"""Implementation of miscelanious functions.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import re

# Explore_SBML_import_export_2020-10-05.ipynb

_map_mathml2numpy = (
# arithmetic operators
    ('abs', 'np.absolute'), ('exp', 'np.exp'), ('sqrt', 'np.sqrt'),
    ('sqr', 'np.square'), ('ln', 'np.log'), ('log10', 'np.log10'),
    ('floor', 'np.floor'), ('ceil', 'np.ceil'),
    ('factorial', 'np.math.factorial'), ('rem', 'np.fmod'),
# relational operators
    ('eq', 'np.equal'), ('neq', 'np.not_equal'), ('gt', 'np.greater'),
    ('lt', 'np.less'), ('geq', 'np.greater_equal'), ('leq', 'np.less_equal'),
# logical operators
    ('and', 'np.logical_and'), ('or', 'np.logical_or'),
    ('xor', 'np.logical_xor'), ('not', 'np.logical_not'),
    ('and', 'np.logical_and'), ('or', 'np.logical_or'),
    ('xor', 'np.logical_xor'), ('not', 'np.logical_not'),
# trigonometric operators
    ('sin', 'np.sin'), ('cos', 'np.cos'), ('tan', 'np.tan'),
    ('sec', '1.0/np.cos'), ('csc', '1.0/np.sin'), ('cot', '1.0/np.tan'),
    ('sinh', 'np.sinh'), ('cosh', 'np.cosh'), ('tanh', 'np.tanh'),
    ('sech', '1.0/np.cosh'), ('csch',' 1.0/np.sinh'), ('coth', '1.0/np.tanh'),
    ('asin', 'np.arcsin'), ('acos', 'np.arccos'),
    ('atan', 'np.arctan'), ('arcsinh', 'np.arcsinh'),
    ('arccosh', 'np.arccosh'), ('arctanh', 'np.arctanh'),
)

def mathml2numpy(mformula):
    """convert mathml infix to a numpy formula.

    This could be converted to a (static) class,
    and it should be possible to set the namespace prefix (default 'np').
    """
    pformula = ' ' + mformula
    pformula = pformula.replace('^', '**')
    pformula = pformula.replace(' && ', ' & ')
    pformula = pformula.replace(' || ', ' | ')
    for mathmlFunction, numpyFunction in _map_mathml2numpy:
        if re.search(r'(?<=\W)' + mathmlFunction + '\(', pformula):
            pformula = (re.sub(r'(?<=\W)' + mathmlFunction + '\(',
                        numpyFunction + '(' , pformula))
    return pformula.strip()


def extract_vps(s):
    # extract parameters from a record and returns these in a dictionary
    # value pairs (key=value) are separated by ','
    # considers nested key value pairs in square brackets (key=[nested vps])
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
    # considers nested key value pairs in square brackets (key=[nested vps])
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
    # considers nested key value pairs in square brackets (key=[nested vps])
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
