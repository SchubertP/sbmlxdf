"""Implementation of Constraints components.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd
import sys

import libsbml

from sbmlxdf.sbase import SBase


class ListOfConstraints(SBase):

    def __init__(self):
        self.constraints = []
        super().__init__()

    def import_sbml(self, sbml_model):
        sbml_lc = sbml_model.getListOfConstraints()
        for sbml_c in sbml_lc:
            c = Constraint()
            c.import_sbml(sbml_c)
            self.constraints.append(c)
        super().import_sbml(sbml_lc)

    def export_sbml(self, sbml_model):
        for c in self.constraints:
            c.export_sbml(sbml_model)
        super().export_sbml(sbml_model.getListOfConstraints())

    def to_df(self):
        return pd.DataFrame([c.to_df() for c in self.constraints])

    def from_df(self, lco_df):
        for idx, co_s in lco_df.iterrows():
            co = Constraint()
            co.from_df(co_s.dropna().to_dict())
            self.constraints.append(co)


class Constraint(SBase):

    def __init__(self):
        self.math = None
        self.message = None
        super().__init__()

    def import_sbml(self, sbml_c):
        self.math = libsbml.formulaToL3String(sbml_c.getMath())
        if sbml_c.isSetMessage():
            self.message = sbml_c.getMessageString()
        super().import_sbml(sbml_c)

    def export_sbml(self, sbml_model):
        sbml_c = sbml_model.createConstraint()
        math = libsbml.parseL3Formula(self.math)
        if math:
            sbml_c.setMath(math)
        else:
            print(libsbml.getLastParseL3Error())
            sys.exit()
        if self.message is not None:
            sbml_c.setMessage(self.message)
        super().export_sbml(sbml_c)

    def to_df(self):
        c_dict = super().to_df()
        c_dict['math'] = self.math
        if self.message is not None:
            xmsg = libsbml.XMLNode.convertStringToXMLNode(self.message)
            if isinstance(xmsg, libsbml.XMLNode) and xmsg.getNumChildren():
                c_dict['message'] = ''
                xp = xmsg.getChild(0)
                for child in range(xp.getNumChildren()):
                    c_dict['message'] += xp.getChild(child).toXMLString().strip()
        return c_dict

    def from_df(self, co_dict):
        self.math = co_dict.get('math', '')
        if 'message' in co_dict:
            msg = ('<message>'
                   '  <p xmlns="http://www.w3.org/1999/xhtml">'
                   '  </p>'
                   '</message> ')
            xmsg = libsbml.XMLNode.convertStringToXMLNode(msg)
            xp = xmsg.getChild('p')
            xcontent = libsbml.XMLNode.convertStringToXMLNode(
                           ' ' + co_dict['message'] + ' ')
            if not xcontent.isEOF():
                xp.addChild(xcontent)
            else:
                for i in range(xcontent.getNumChildren()):
                    xp.addChild(xcontent.getChild(i))
            self.message = xmsg.toXMLString()
        super().from_df(co_dict)
