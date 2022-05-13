"""Implementation of miscellaneous functions.

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
    ('sech', '1.0/NP_NS.cosh'), ('csch', ' 1.0/NP_NS.sinh'),
    ('coth', '1.0/NP_NS.tanh'),
    ('asin', 'NP_NS.arcsin'), ('acos', 'NP_NS.arccos'),
    ('atan', 'NP_NS.arctan'), ('arcsinh', 'NP_NS.arcsinh'),
    ('arccosh', 'NP_NS.arccosh'), ('arctanh', 'NP_NS.arctanh'),
)


def mathml2numpy(mformula, np_ns='np'):
    """Convert mathml infix notation to a numpy notation

    mathml functions and operators are converted to numpy equivalents,
    where possible. Functions are prefixed with numpy namespace

    :param mformula: mathml infix notation extracted from SBML
    :type mformula: str
    :param np_ns: numpy namespace prefix used in own Python code. Default: 'np'
    :type np_ns: str
    :returns: mathml converted to numpy notation
    :rtype: str
    """
    np_formula = ' ' + mformula
    np_formula = re.sub(r'\s?dimensionless\s?', ' ', np_formula)
    np_formula = re.sub(r'\^', '**', np_formula)
    np_formula = re.sub(r'\s?&&\s?', ' & ', np_formula)
    np_formula = re.sub(r'\s?\|\|\s?', ' | ', np_formula)
    for mathml_f, np_f in _map_mathml2numpy:
        np_formula = re.sub(r'\s+' + mathml_f + r'\(',
                            ' ' + np_f.replace('NP_NS', np_ns) + '(',
                            np_formula)
    return np_formula.strip()


def get_bool_val(parameter):
    """Get boolean value from parameter

    Values imported from spreadsheets are all converted to string
    objects, while parameters coming from Model.to_df() may contain
    boolean values.
    'True' objects from spreadsheets can be represented as
    'True' or as numerical 1, getting converted to string.

    :param parameter: parameter to retrieve boolean value from
    :type parameter: bool or str
    :returns: boolean value of parameter
    :rtype: bool
    """
    if type(parameter) == bool:
        return parameter
    else:
        return parameter.upper() == str('TRUE') or parameter == '1'


def record_generator(records_str, sep=';'):
    """Generator to extract individual records from a string of records.

       This generator does not yet handle nested records.

    :param records_str: containing records separated by sep
    :type records_str: str
    :param sep: seperator used to separate records
    :type sep: str (default: ';')
    :returns: key-values pairs extracted from record
    :rtype: dict
    """
    if type(records_str) == str:
        for record in records_str.split(sep):
            if len(record.strip()) > 0:
                yield record.strip()


def extract_params(record):
    """Extract parameters from a record.

    A single record consists of comma separated key-value pairs.
    Example: 'key1=val1, key2=val2, ...' is converted to
    {key1: val1, key2: val2, ...}

    :param record: key '=' value pairs separated by ","
    :type record: str
    :returns: key-values pairs extracted from record
    :rtype: dict
    """
    params = {}
    for kv_pair in record_generator(record, sep=','):
        if '=' in kv_pair:
            k, v = kv_pair.split('=')
            params[k.strip()] = v.strip()
    return params


def extract_nested_params(s):
    """Extract parameters from a record.

    A record consists of comma separated key-value pairs.
    Values may contain nested records (key=[record_x, record_y, ...]),
    values can also be functions with several parameters, e.g.
    math=gamma(shape_Z, scale_Z)

    Example: 'key1=val1, key2=val2, ...' is converted to
    {key1: val1, key2: val2, ...}

    see also: :func:`extract_records` and :func:`extract_lo_records`

    :param s: key '=' value pairs separated by ","
    :type s: str
    :returns: key-values pairs
    :rtype: dict
    """
    find_key = re.compile(r'\s*(?P<key>\w*)\s*=\s*')
    params = {}
    pos = 0
    i = 0
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
                        if i == len(s) - 1:
                            i += 1
                params[m['key']] = s[pos:i].strip()
                pos = i
        else:
            break
    return params


def extract_records(s):
    """Split string of records into individual records.

    Each record consists of comma separated key-value pairs.
    E.g. record1: 'key1=val1, key2=val2, ...'.
    Values may contain nested records (key=[record_x, record_y, ...]).

    Example: 'record1; record2; ...' is converted to [record1, record2, ...]

    see also: :func:`extract_params` and :func:`extract_lo_records`

    :param s: records separated by ";"
    :type s: str
    :returns: elements contain individual records
    :rtype: list of str
    """
    records = []
    brackets = 0
    pos = 0
    i = 0
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
        pos = i + 1
    return records


def extract_lo_records(s):
    """Split string of groups of records into strings of records per group.

    Supporting values with containing nested records
    (key=[record_x, record_y, ...]).

    Example: '[record1; record2; ...];[record7; record8; ...]' is
    converted to ['record1; record2; ...', 'record7; record8; ...']

    see also: :func:`extract_params` and :func:`extract_records`

    :param s: string with groups of records enclosed in square brackets, separated by ";"
    :type s: str
    :returns: elements contain the string of records for each group
    :rtype: list of str
    """
    lo_records = []
    pos = 0
    i = 0
    while pos < len(s):
        m = re.search(r'\[', s[pos:])
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
            pos = i + 1
        else:
            break
    return lo_records


def extract_xml_attrs(xml_annots, ns=None, token=None):
    """Extract XML-attributes from given namespace and/or token.

    Example of xml_annots: 'ns_uri=http://www.hhu.de/ccb/bgm/ns, prefix=bgm,
    token=molecule, weight_Da=100'

    :param xml_annots: XML-annotations separated by ";"
    :type xml_annots: str
    :param ns: namespace from which to collect attributes
    :type ns: str, optional
    :param token: token from which to collect attributes
    :type token: str, optional
    :returns: attribute names corresponding values
    :rtype: dict
    """
    xml_attrs = {}
    for xml_str in record_generator(xml_annots):
        params = extract_params(xml_str)
        if (((ns is not None) and (params['ns_uri'] != ns)) or
                ((token is not None) and (params['token'] != token))):
            continue
        for k, v in params.items():
            if k not in {'ns_uri', 'prefix', 'token'}:
                xml_attrs[k] = v
    return xml_attrs


def convert_srefs(srefs_str):
    """Convert species references from rectants/products.

    E.g. 'species=M_mal__L_e, stoic=1.0, const=True; species=M_h_e, stoic=2.0, const=True'
    gets converted to '2.0 M_h_e + M_mal__L_e'
    srefs get sorted according to metabolite id

    :param srefs_str: ';'-separated string with species references as key/value pairs
    :type srefs_str: str
    :returns: stoichiometric string
    :rtype: string
    """
    d_srefs = {}
    for sref in record_generator(srefs_str):
        params = extract_params(sref)
        d_srefs[params['species']] = params.get('stoic', '1.0')

    l_srefs = []
    for sid in sorted(d_srefs.keys()):
        if d_srefs[sid] == '1.0':
            l_srefs.append(sid)
        else:
            l_srefs.append(d_srefs[sid] + ' ' + sid)
    return ' + '.join(l_srefs)


def generate_srefs(stoichometric_str):
    """Generate species references from one side of reaction string.

    E.g. '2.0 M_h_e + M_mal__L_e' gets converted to
    'species=M_h_e, stoic=2.0, const=True; species=M_mal__L_e, stoic=1.0, const=True'

    :param stoichometric_str: stoichiometric string
    :type stoichometric_str: str
    :returns: ';'-separated string with species references as key/value pairs
    :rtype: string
    """
    d_srefs = {}
    for sref in stoichometric_str.split('+'):
        l_sref = re.split(r'\s+', sref.strip())
        stoic = l_sref[0] if len(l_sref) == 2 else '1.0'
        sid = l_sref[-1]
        if sid != '':
            d_srefs[sid] = stoic
    l_srefs = []
    for sid, stoic in d_srefs.items():
        l_srefs.append('species=' + sid + ', stoic=' + stoic + ', const=True')
    return '; '.join(l_srefs)


def add_reaction_translations(model_dict):
    """Applies translations to some reaction columns.

    To support analysis of reactions table.
    Translations implemented are:
    - given the numberical value of flux bounds.
    - adding a reaction string

    :param model_dict: pandas DataFrames of model components
    :type model_dict: dict
    :returns: updated reactions table
    :rtype: pandas DataFrame
    """
    df_reactions = model_dict['reactions'].copy()

    if 'reactants' in df_reactions.columns and 'products' in df_reactions.columns:
        for rid, row in df_reactions.iterrows():
            direction = ' -> ' if row['reversible'] is True else ' => '
            df_reactions.at[rid, 'reactionString'] = (convert_srefs(row['reactants'])
                                                      + direction
                                                      + convert_srefs(row['products']))
    if ('parameters' in model_dict and
            'fbcLowerFluxBound' in df_reactions.columns and
            'fbcUpperFluxBound' in df_reactions.columns):
        params = model_dict['parameters']['value'].to_dict()
        df_reactions['fbcLb'] = df_reactions['fbcLowerFluxBound'].replace(params)
        df_reactions['fbcUb'] = df_reactions['fbcUpperFluxBound'].replace(params)

    return df_reactions


def translate_reaction_string(df_reactions):
    """Produces reactants and products from reaction string.

    To support defining reactants and products with in a more readable format.
    Used, e.g. when reactants/products not defined in the dataframe
    e.g. 'M_fum_c + M_h2o_c -> M_mal__L_c' for a reversible reaction
    e.g. 'M_ac_e => ' for an irreversible reaction with no product

    :param df_reactions: pandas DataFrames of reaction objects
    :type df_reactions: dataframe
    :returns: updated reactions table
    :rtype: pandas DataFrame
    """
    df_reactions = df_reactions.copy()

    for rid, reaction_string in df_reactions['reactionString'].items():
        if type(reaction_string) is str:
            if ('->' in reaction_string) or ('=>' in reaction_string):
                components = re.split(r'[=-]>', reaction_string)
            else:  # actually an error
                components = ['', '']
            df_reactions.at[rid, 'reversible'] = ('->' in reaction_string)
            df_reactions.at[rid, 'reactants'] = generate_srefs(components[0])
            df_reactions.at[rid, 'products'] = generate_srefs(components[1])
    return df_reactions
