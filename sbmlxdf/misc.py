"""Implementation of miscellanious functions.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import re
import libsbml

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
    """Convert mathml infix notation to a numpy formula.

    Prefixes math functions with a numpy prefix.
    mathml functions are converted to numpy equivalenta where possible.

    Parameters
    ----------
    mformula : str
        String with mathml infix notation extracted from SBML,
        e.g. collected from a math element.

    np_ns : str, optional
        numpy namespace prefix used in own Python code.
        Default: 'np'

    Returns
    -------
    str
        containing mathml operators and functions converted
        to numpy notation. Sting could be further processed and
        converted to a numpy function.

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
    """Extract parameters from a record.

    Parameters
    ----------
    s : str
        record string containting key-value pairs 'key=value' separated by ','.
        e.g. 'key1=value1, key2=value2, key3=value3'.
        wWhite space chars are removed.
        Nested records must be in square brackets (key=[nested records]).
        Values can also be functions, e.g. math=gamma(shape_Z, scale_Z).

    Returns
    -------
    dict
        keys and values extracted from record

    """
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
                    r_brackets = 0
                    for i in range(pos, len(s)):
                        if s[i] == '(':
                            r_brackets += 1
                        if s[i] == ')':
                            r_brackets -= 1
                        if s[i] == ',' and r_brackets == 0:
                            break
                        if i == len(s)-1:
                            i += 1
                params[m['key']] = s[pos:i].strip()
                pos = i
        else:
            break
    return params


def extract_records(s):
    """Split group of records considering nesting.

    Used for complicated Uncertainty definitions.

    Parameters
    ----------
    s : str
        String with group of records that are separated by ';',
        e.g. 'record1; record2; record3', where records
        consist of comma separated key-value pairs.
        Nested records must be in square brackets (key=[nested records])

    Returns
    -------
    list
        list with strings of individual records, 
        which can be processed by extract_params()

    """
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
    """Split groups of groups of records considering nesting.

    Used for complicated Uncertainty definitions.

    Parameters
    ----------
    s : str
        string with groups of groups of records, that are
        enclosed in square brackets and separated by ';',
        e.g. '[record1; record2; ...];[record7; record8; ...]'
        Nested records must be in square brackets (key=[nested records])

    Returns
    -------
    list
        list with strings of group of records,
        which can be processed by extract_records()

    """
    # extract list of records from a list of list of records
    # list of records are enclosed by square brackets and separated by ';'
    # "v
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


def extract_xml_attrs(xml_annots, ns=None, token=None):
    """Extract attributes from string for given namespace and/or token.

    Parameters
    ----------
    xml_annots : str
        xml-annotation string. Can be a sequence of XML-annotations
        separated by ';'
        e.g. 'ns_uri=http://www.hhu.de/ccb/bgm/ns, prefix=bgm,
        token=molecule, weight_Da=100'

    ns : str (optional)
        namespace for which attributes should be collected.
        e.g. 'http://www.hhu.de/ccb/bgm/ns'

    token : str
        token for which attributes should be collected.
        e.g. 'molecule'

    Returns
    -------
    dict
        Keys are attribute names and values are attributes values

    """
    xml_attrs = {}
    for xml_str in xml_annots.split(';'):
        params = extract_params(xml_str)
        if (((ns != None) and (params['ns_uri'] != ns)) or
            ((token != None) and (params['token'] != token))):
            continue
        for k, v in params.items():
            if k not in {'ns_uri', 'prefix', 'token'}:
                xml_attrs[k] = v
    return xml_attrs
