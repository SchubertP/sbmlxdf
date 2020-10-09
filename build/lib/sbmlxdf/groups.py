"""Implementation of Groups ext. package components.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd

import libsbml

from .sbase import SBase
from .misc import extract_vps

# Explore_SBML_import_export_2020-10-05.ipynb

class GroupsListOfGroups(SBase):

    def __init__(self):
        self.groups = []
        super().__init__()

    def import_sbml(self, sbml_model):
        groups_plugin = sbml_model.getPlugin('groups')
        sbml_lg = groups_plugin.getListOfGroups()
        for sbml_g in sbml_lg:
            g = GroupsGroup()
            g.import_sbml(sbml_g)
            self.groups.append(g)
        super().import_sbml(sbml_lg)

    def export_sbml(self, sbml_model):
        groups_plugin = sbml_model.getPlugin('groups')
        for group in self.groups:
            group.export_sbml(groups_plugin)
        super().export_sbml(groups_plugin.getListOfGroups())

    def to_df(self):
        return pd.DataFrame([g.to_df() for g in self.groups])

    def from_df(self, lg_df):
        for idx, g_s in lg_df.iterrows():
            g = GroupsGroup()
            g.from_df(g_s.dropna().to_dict())
            self.groups.append(g)


class GroupsGroup(SBase):

    def __init__(self):
        super().__init__()

    def import_sbml(self, sbml_g):
        self.kind = sbml_g.getKindAsString()
        if sbml_g.getNumMembers():
            self.lo_members = GroupListOfMembers()
            self.lo_members.import_sbml(sbml_g)
        super().import_sbml(sbml_g)

    def export_sbml(self, groups_plugin):
        sbml_g = libsbml.Group()
        sbml_g.setKind(self.kind)
        if hasattr(self, 'lo_members'):
            self.lo_members.export_sbml(sbml_g)
        super().export_sbml(sbml_g)
        groups_plugin.addGroup(sbml_g)

    def to_df(self):
        g_dict = super().to_df()
        g_dict['kind'] = self.kind
        if hasattr(self, 'lo_members'):
            for key, val in self.lo_members.to_df().items():
                g_dict[key] = val
        return g_dict

    def from_df(self, gr_dict):
        if 'kind' in gr_dict:
            self.kind = gr_dict['kind']
        if GroupListOfMembers.is_in_df(gr_dict):
            self.lo_members = GroupListOfMembers()
            self.lo_members.from_df(gr_dict)
        super().from_df(gr_dict)


class GroupListOfMembers(SBase):

    def __init__(self):
        self.members = []
        super().__init__()

    def import_sbml(self, sbml_g):
        sbml_lm = sbml_g.getListOfMembers()
        for sbml_m in sbml_g.getListOfMembers():
            m = GroupMember()
            m.import_sbml(sbml_m)
            self.members.append(m)
        super().import_sbml(sbml_lm)

    def export_sbml(self, sbml_g):
        for m in self.members:
            m.export_sbml(sbml_g)
        sbml_lm = sbml_g.getListOfMembers()
        super().export_sbml(sbml_lm)

    def to_df(self):
        attr = []
        if hasattr(self, 'id'):
            attr.append('id=' + self.id)
        if hasattr(self, 'name'):
            attr.append('name=' + self.name)
        if hasattr(self, 'sboterm'):
            attr.append('sboterm=' + self.sboterm)
        lm_dict={'listMembers': ', '.join(attr)}
        lm_dict['members'] = '; '.join([m.to_df() for m in self.members])
        return lm_dict

    def is_in_df(gr_dict):
        return len({'listMembers', 'members'}.intersection(gr_dict.keys()))

    def from_df(self, gr_dict):
        if 'listMembers' in gr_dict:
            attr_dict = extract_vps(gr_dict['listMembers'])
            if 'id' in attr_dict:
                self.id = attr_dict['id']
            if 'name' in attr_dict:
                self.name = attr_dict['name']
            if 'sboterm' in attr_dict:
                self.sboterm = attr_dict['sboterm']
        for m_str in gr_dict['members'].split(';'):
            m = GroupMember()
            m.from_df(m_str)
            self.members.append(m)


class GroupMember(SBase):

    def __init__(self):
        super().__init__()

    def import_sbml(self, sbml_m):
        if sbml_m.isSetIdRef():
            self.idref = sbml_m.getIdRef()
        if sbml_m.isSetMetaIdRef():
            self.metaidref = sbml_m.getMetaIdRef()
        super().import_sbml(sbml_m)

    def export_sbml(self, sbml_g):
        sbml_m = libsbml.Member()
        if hasattr(self, 'idref'):
            sbml_m.setIdRef(self.idref)
        if hasattr(self, 'metaidref'):
            sbml_m.setMetaIdRef(self.metaidref)
        super().export_sbml(sbml_m)
        sbml_g.addMember(sbml_m)

    def to_df(self):
        attr = []
        if hasattr(self, 'idref'):
            attr.append('idRef=' + self.idref)
        if hasattr(self, 'metaidref'):
            attr.append('metaIdRef=' + self.metaidref)
        if hasattr(self, 'id'):
            attr.append('id=' + self.id)
        if hasattr(self, 'name'):
            attr.append('name=' + self.name)
        if hasattr(self, 'sboterm'):
            attr.append('sboterm=' + self.sboterm)
        return ', '.join(attr)

    def from_df(self, m_str):
        m_dict = extract_vps(m_str)
        if 'idRef' in m_dict:
            self.idref = m_dict['idRef']
        if 'metaIdRef' in m_dict:
            self.metaidref = m_dict['metaIdRef']
        if 'id' in m_dict:
            self.id = m_dict['id']
        if 'name' in m_dict:
            self.name = m_dict['name']
        if 'sboterm' in m_dict:
            self.sboterm = m_dict['sboterm']
