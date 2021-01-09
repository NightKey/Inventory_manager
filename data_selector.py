import PySimpleGUI as sg
import threading, time, core
from product_editor import editor

translator = None

class selector:
    PERSON_SELECTOR = 0
    PRODUCT_SELECTOR = 1
    NONAME_PRODUCTS = 2

    def __init__(self, call_back, _type=0, data=None, pre_set=None):
        global translator
        from core import translator
        """Enables searching for data. Either for persons, or for products.
        """
        self.is_running = True
        self.type = _type
        self.pre_set = pre_set
        self.data = data[:100] if self.type == selector.NONAME_PRODUCTS else core.products[:100] if self.type == selector.PRODUCT_SELECTOR else core.persons[:100]
        if _type == selector.PRODUCT_SELECTOR:
            layout_top = [
                [sg.Text(translator.translate('ds_001'))],
                [sg.Text(f"{translator.translate('ds_002')}: "), sg.In(key="PRODUCT_NO", enable_events=True, size=(10, 1)), sg.Text("X", key="PRODUCT_NO_DELETE", enable_events=True), sg.Text(f"{translator.translate('ds_003')}: "), sg.In(key="PRODUCT_NAME", enable_events=True, size=(25, 1)), sg.Text("X", key="PRODUCT_NAME_DELETE", enable_events=True)],
                [sg.Listbox(values=(self.data[:100] if len(self.data) > 100 else self.data), enable_events=True, key="PRODUCT_SHOW", size=(70, 25))]
            ]
            buttons = [
                [sg.Button(translator.translate('g_finish'), key="CANCEL")]
            ]
        elif _type == selector.PERSON_SELECTOR:
            layout_top= [
                [sg.Text(translator.translate('ds_004'))],
                [sg.Text(f"{translator.translate('ds_005')}: "), sg.In(key="PERSON", enable_events=True), sg.Text("X", key="PERSON_DELETE", enable_events=True)],
                [sg.Listbox(values=(self.data[:100] if len(self.data) > 100 else self.data), enable_events=True, key="PERSON_SHOW", size=(70, 25))]
            ]
            buttons = [
                [sg.Button(translator.translate('g_cancel'), key="CANCEL"), sg.Button(translator.translate('g_select'), key="SELECT")]
            ]
        elif _type == selector.NONAME_PRODUCTS:
            layout_top = [
                [sg.Text(translator.translate('ds_006'))],
                [sg.Listbox(values=(self.data[:100] if len(self.data) > 100 else self.data), enable_events=True, key="PRODUCT_SHOW", size=(70, 25))]
            ]
            buttons = [
                [sg.Button(translator.translate('g_finish'), key="CANCEL")]
            ]
        layout = [
            [sg.Column(layout_top)],
            [sg.Column(buttons)]
        ]
        self.window = sg.Window(translator.translate('ds_007'), layout, finalize=True, return_keyboard_events=True)
        self.call_back = call_back
        self.read = self.window.read
        self.product_editor = None

    def Close(self):
        self.window.Close()
        if self.product_editor is not None and self.product_editor.is_running:
            self.product_editor.Close()
        self.is_running = False

    def product_edited(self, new):
        pass

    def work(self, event, values):
        if event in ["PRODUCT_NO_DELETE", "PRODUCT_NAME_DELETE", "PERSON_DELETE"]:
            event = event.replace("_DELETE", '')
            self.window[event].Update("")
            values[event] = ""
        if event == "Escape:27" or event == sg.WIN_CLOSED or event == "CANCEL":
            self.Close()
        elif event == "PRODUCT_NAME" or event == "PRODUCT_NO":
            self.data = core.search_for(core.PRODUCT, [values["PRODUCT_NO"], values["PRODUCT_NAME"]])
            if len(self.data) > 100: self.data = self.data[:100]
            self.window["PRODUCT_SHOW"].update(self.data)
        elif event == "Down:40":
            key = "PERSON_SHOW" if self.type == selector.PERSON_SELECTOR else "PRODUCT_SHOW"
            print(self.window[key].GetIndexes())
            index = self.window[key].GetIndexes()[-1] if self.window[key].GetIndexes() != () else -1
            _max = len(self.data)
            self.window[key].Update(scroll_to_index=index+1 if index < _max-1 else 0)
            self.window[key].Update(set_to_index=index+1 if index < _max-1 else 0)
        elif event == "Up:38":
            key = "PERSON_SHOW" if self.type == selector.PERSON_SELECTOR else "PRODUCT_SHOW"
            index = self.window[key].GetIndexes()[-1] if self.window[key].GetIndexes() != () else _max
            _max = len(self.data)
            self.window[key].Update(scroll_to_index=index+1 if index > 0 else _max-1)
            self.window[key].Update(set_to_index=index+1 if index > 0 else _max-1)
        elif event == "PERSON" and values["PERSON"] != "":
            self.data = core.search_for(core.PERSON, values["PERSON"])
            if len(self.data) > 100: self.data = self.data[:100]
            self.window["PERSON_SHOW"].update(self.data)
        elif event == "PRODUCT_SHOW":
            try:
                if self.product_editor is not None and self.product_editor.is_running:
                    self.product_editor.Close()
                if self.call_back is not None:
                    self.product_editor = editor(values["PRODUCT_SHOW"][0], self.call_back, True, self.pre_set)
                else:
                    self.product_editor = editor(values["PRODUCT_SHOW"][0], self.product_edited, False)
            except Exception as ex: print(f"{type(ex)} --> {ex}")
        elif event == "PERSON_SHOW":
            if self.call_back == None:
                try:
                    if self.product_editor is not None and self.product_editor.is_running:
                        self.product_editor.Close()
                    from note_lister import lister
                    tmp = core.search_for([core.QUOTATION, core.DELIVERY_NOTE, core.ORDER], values["PERSON_SHOW"][0])
                    if tmp == []:
                        sg.popup_auto_close(translator.translate('g_no_data'), title=translator.translate('g_alert'))
                        return
                    self.product_editor = lister(tmp, values["PERSON_SHOW"][0].name, None)
                except Exception as ex: print(f"{type(ex)} --> {ex}")
        elif event == "SELECT":
            if self.call_back != None:
                self.call_back(values["PERSON_SHOW"][0] if self.type == selector.PERSON_SELECTOR else None)
                self.Close()
        if self.product_editor != None and self.product_editor.is_running:
            pevent, pvalues = self.product_editor.read(timeout=10)
            self.product_editor.work(pevent, pvalues)
        elif self.product_editor != None:
            self.product_editor = None

    def timed(self, event, values):
        start = time.process_time()
        self.work(event, values)
        end = time.process_time()
        print(f"{event} took {end-start} s")

    def show(self):
        while not self.window.was_closed():
            event, values = self.read(timeout=0)
            self.timed(event, values)
            

if __name__=="__main__":
    core.startup()
    sc = selector(None, 1)
    sc.show()
