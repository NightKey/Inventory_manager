import PySimpleGUI as sg
from data_selector import selector
from core import DELIVERY_NOTE, ORDER, QUOTATION

class create:
    def __init__(self, _type):
        self.type = _type
        layout = [
            
        ]

if event == "PERSON_SHOW":
    keys = [DELIVERY_NOTE if self.type <= DELIVERY_NOTE else None,
            ORDER if self.type <= ORDER else None,
            QUOTATION if self.type <= QUOTATION else None]
    try: keys.remove(None)
    except: pass
    if len(keys) == 1:
        keys = keys[0]
    elif len(keys) == 0:
        return
    self.importer = from_note(core.search_for(keys, *values['PERSON_SHOW']), self.import_from)
if self.importer != None and self.importer.is_running:
            ievent, ivalues = self.importer.read()
            self.importer.work(ievent, ivalues)