"""Implementation of Events components.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd
import sys

import libsbml

from sbmlxdf.sbase import SBase
from sbmlxdf.misc import extract_params


class ListOfEvents(SBase):

    def __init__(self):
        self.events = []
        super().__init__()

    def import_sbml(self, sbml_model):
        sbml_le = sbml_model.getListOfEvents()
        for sbml_e in sbml_le:
            e = Event()
            e.import_sbml(sbml_e)
            self.events.append(e)
        super().import_sbml(sbml_le)

    def export_sbml(self, sbml_model):
        for e in self.events:
            e.export_sbml(sbml_model)
        super().export_sbml(sbml_model.getListOfEvents())

    def to_df(self):
        return pd.DataFrame([e.to_df() for e in self.events])

    def from_df(self, le_df):
        for idx, e_s in le_df.iterrows():
            e = Event()
            e.from_df(e_s.dropna().to_dict())
            self.events.append(e)


class Event(SBase):

    def __init__(self):
        self.event_assignments = {}
        super().__init__()

    def import_sbml(self, sbml_e):
        self.from_trigger_time = sbml_e.getUseValuesFromTriggerTime()
        self.trigger = Trigger()
        self.trigger.import_sbml(sbml_e)
        if sbml_e.isSetPriority():
            self.priority = Priority()
            self.priority.import_sbml(sbml_e)
        if sbml_e.isSetDelay():
            self.delay = Delay()
            self.delay.import_sbml(sbml_e)
        for sbml_ea in sbml_e.getListOfEventAssignments():
            ea = EventAssignment()
            ea.import_sbml(sbml_ea)
            self.event_assignments[ea.variable] = ea
        super().import_sbml(sbml_e)

    def export_sbml(self, sbml_model):
        sbml_e = sbml_model.createEvent()
        sbml_e.setUseValuesFromTriggerTime(self.from_trigger_time)
        self.trigger.export_sbml(sbml_e)
        if hasattr(self, 'priority'):
            self.priority.export_sbml(sbml_e)
        if hasattr(self, 'delay'):
            self.delay.export_sbml(sbml_e)
        for ea in self.event_assignments.values():
            ea.export_sbml(sbml_e)
        super().export_sbml(sbml_e)

    def to_df(self):
        e_dict = super().to_df()
        e_dict['valFromTriggerTime'] = self.from_trigger_time
        for key, val in self.trigger.to_df().items():
            e_dict[key] = val
        if hasattr(self, 'priority'):
            for key, val in self.priority.to_df().items():
                e_dict[key] = val
        if hasattr(self, 'delay'):
            for key, val in self.delay.to_df().items():
                e_dict[key] = val
        if len(self.event_assignments):
            e_dict['eventAssign'] = '; '.join([
                           ea.to_df()
                           for ea in self.event_assignments.values()
                           ])
        return e_dict

    def from_df(self, e_dict):
        self.from_trigger_time = (e_dict['valFromTriggerTime']==str(True) or
                                  e_dict['valFromTriggerTime']=='1')
        self.trigger = Trigger()
        self.trigger.from_df(e_dict)
        if Priority.is_in_df(e_dict):
            self.priority = Priority()
            self.priority.from_df(e_dict)
        if Delay.is_in_df(e_dict):
            self.delay = Delay()
            self.delay.from_df(e_dict)
        if 'eventAssign' in e_dict:
            for ea_str in e_dict['eventAssign'].split(';'):
                ea = EventAssignment()
                ea.from_df(ea_str)
                self.event_assignments[ea.variable] = ea
        super().from_df(e_dict)


class Trigger(SBase):

    def __init__(self):
        super().__init__()

    def import_sbml(self, sbml_e):
        sbml_t = sbml_e.getTrigger()
        self.init_val = sbml_t.getInitialValue()
        self.persistent = sbml_t.getPersistent()
        self.math = libsbml.formulaToL3String(sbml_t.getMath())
        super().import_sbml(sbml_t)

    def export_sbml(self, sbml_e):
        sbml_t = sbml_e.createTrigger()
        sbml_t.setInitialValue(self.init_val)
        sbml_t.setPersistent(self.persistent)
        math = libsbml.parseL3Formula(self.math)
        if math:
            sbml_t.setMath(math)
        else:
            print(libsbml.getLastParseL3Error())
            sys.exit()
        super().export_sbml(sbml_t)

    def to_df(self):
        tr_dict = {}
        tr_dict['triggerInitVal'] = self.init_val
        tr_dict['triggerPersistent'] = self.persistent
        tr_dict['triggerMath'] = self.math
        if hasattr(self, 'sboterm'):
            tr_dict['triggerSboTerm'] = self.sboterm
        return tr_dict

    def from_df(self, e_dict):
        self.init_val = (e_dict['triggerInitVal']==str(True) or
                         e_dict['triggerInitVal']=='1')
        self.persistent = (e_dict['triggerPersistent']==str(True) or
                           e_dict['triggerPersistent']=='1')
        self.math = e_dict['triggerMath']
        if 'triggerSboTerm' in e_dict:
            self.sboterm = e_dict['triggerSboTerm']


class Priority(SBase):

    def __init__(self):
        super().__init__()

    def import_sbml(self, sbml_e):
        sbml_p = sbml_e.getPriority()
        self.math = libsbml.formulaToL3String(sbml_p.getMath())
        super().import_sbml(sbml_p)

    def export_sbml(self, sbml_e):
        sbml_p = sbml_e.createPriority()
        math = libsbml.parseL3Formula(self.math)
        if math:
            sbml_p.setMath(math)
        else:
            print(libsbml.getLastParseL3Error())
            sys.exit()
        super().export_sbml(sbml_p)

    def to_df(self):
        pr_dict = {}
        pr_dict['priorityMath'] = self.math
        if hasattr(self, 'sboterm'):
            pr_dict['prioritySboTerm'] = self.sboterm
        return pr_dict

    def is_in_df(e_dict):
        return 'priorityMath' in e_dict

    def from_df(self, e_dict):
        self.math = e_dict['priorityMath']
        if 'prioritySboTerm' in e_dict:
            self.sboterm = e_dict['prioritySboTerm']


class Delay(SBase):

    def __init__(self):
        super().__init__()

    def import_sbml(self, sbml_e):
        sbml_d = sbml_e.getDelay()
        self.math = libsbml.formulaToL3String(sbml_d.getMath())
        super().import_sbml(sbml_d)

    def export_sbml(self, sbml_e):
        sbml_d = sbml_e.createDelay()
        math = libsbml.parseL3Formula(self.math)
        if math:
            sbml_d.setMath(math)
        else:
            print(libsbml.getLastParseL3Error())
            sys.exit()
        super().export_sbml(sbml_d)

    def to_df(self):
        de_dict = {}
        de_dict['delayMath'] = self.math
        if hasattr(self, 'sboterm'):
            de_dict['delaySboTerm'] = self.sboterm
        return de_dict

    def is_in_df(e_dict):
        return 'delayMath' in e_dict

    def from_df(self, de_dict):
        self.math = de_dict['delayMath']
        if 'delaySboTerm' in de_dict:
            self.sboterm = de_dict['delaySboTerm']


class EventAssignment(SBase):

    def __init__(self):
        super().__init__()

    def import_sbml(self, sbml_ea):
        self.variable = sbml_ea.getVariable()
        self.math = libsbml.formulaToL3String(sbml_ea.getMath())
        super().import_sbml(sbml_ea)

    def export_sbml(self, sbml_e):
        sbml_ea = sbml_e.createEventAssignment()
        sbml_ea.setVariable(self.variable)
        math = libsbml.parseL3Formula(self.math)
        if math:
            sbml_ea.setMath(math)
        else:
            print(libsbml.getLastParseL3Error())
            sys.exit()
        super().export_sbml(sbml_ea)

    def to_df(self):
        attr = ['variable=' + self.variable,
                'math=' + self.math]
        if hasattr(self, 'sboterm'):
            attr.append('sboterm=' + self.sboterm)
        return ', '.join(attr)

    def from_df(self, ea_str):
        ea_dict = extract_params(ea_str)
        if 'variable' in ea_dict:
            self.variable = ea_dict['variable']
        if 'math' in ea_dict:
            self.math = ea_dict['math']
        if 'sboterm' in ea_dict:
            self.sboterm = ea_dict['sboterm']
