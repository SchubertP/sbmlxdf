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


def extract_vps(record):
    # split record in parts by '=' and not ',', to allow for commas in value
    # first part contains first key
    # next parts contain:
    #       value (corresponding to previous key),
    #       attribute separator ','
    #       next key
    # last part contains value corresponding to last key
    # addtional white spaces are being removed
    part = record.split('=')
    key = []
    val = []
    key.append(part[0].strip())
    for i in range(1, len(part)-1):
        m = re.match(r'^\s*(?P<val>.*)\s*,\s*(?P<next_key>\w+)\s*$', part[i])
        if m:
            val.append(m['val'])
            key.append(m['next_key'])
    val.append(part[-1].strip())
    return dict(zip(key,val))


def extract_uncertainty(s):
    # extracts from string next Uncertainty, enclosed in square brackets
    # Uncertanty consist of UncertParameters separated by ';'
    # starting behind the opening bracket, looking for corresonding closing
    #  bracket. Returning this string of UncerParameters,
    #  not including closing brackets
    brackets = 1
    for i in range(len(s)):
        if s[i] == '[':
            brackets += 1
        if s[i] == ']':
            brackets -= 1
        if brackets == 0:
            return s[:i]
    return s


def extract_uncert_parameter(s):
    # from sting of UncertParameters (separated by ';') next UncertParameter.
    # UncertParameters can contain nested ListOfUncertParameters '[...]'
    # read up to next ';', considering nested ListOfUncertParameters
    brackets = 0
    for i in range(len(s)):
        if s[i] == '[':
            brackets += 1
        if s[i] == ']':
            brackets -= 1
        if s[i] == ';' and brackets == 0:
            return s[:i]
    return s
