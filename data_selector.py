import PySimpleGUI as sg
import threading, time, core
from product_editor import editor

class selector:
    PERSON_SELECTOR = 0
    PRODUCT_SELECTOR = 1
    NONAME_PRODUCTS = 2

    def __init__(self, call_back, _type=0, pre_set=None):
        """Enables searching for data. Either for persons, or for products.
        """
        self.is_running = True
        self.type = _type
        self.pre_set = pre_set
        if _type == selector.PRODUCT_SELECTOR:
            layout_top = [
                [sg.Text("Árucikk kereső")],
                [sg.Text("Cikkszám: "), sg.In(key="PRODUCT_NO", enable_events=True, size=(10, 1)), sg.Text("X", key="PRODUCT_NO_DELETE", enable_events=True), sg.Text("Cikk leírás: "), sg.In(key="PRODUCT_NAME", enable_events=True, size=(25, 1)), sg.Text("X", key="PRODUCT_NAME_DELETE", enable_events=True)],
                [sg.Listbox(values=(core.products[:100] if len(core.products) > 100 else core.products), enable_events=True, key="PRODUCT_SHOW", size=(70, 25))]
            ]
            buttons = [
                [sg.Button("Kész", key="CANCEL")]
            ]
        elif _type == selector.PERSON_SELECTOR:
            layout_top= [
                [sg.Text("Személy kereső")],
                [sg.Text("Név: "), sg.In(key="PERSON", enable_events=True)],
                [sg.Listbox(values=(core.persons[:100] if len(core.persons) > 100 else core.persons), enable_events=True, key="PERSON_SHOW", size=(70, 25))]
            ]
            buttons = [
                [sg.Button("Mégsem", key="CANCEL"), sg.Button("Kiválaszt", key="SELECT")]
            ]
        elif _type == selector.NONAME_PRODUCTS:
            layout_top = [
                [sg.Text("Árucikk listázó")],
                [sg.Listbox(values=(pre_set[:100] if len(pre_set) > 100 else pre_set), enable_events=True, key="PRODUCT_SHOW", size=(70, 25))]
            ]
            buttons = [
                [sg.Button("Kész", key="CANCEL")]
            ]
        layout = [
            [sg.Column(layout_top)],
            [sg.Column(buttons)]
        ]
        self.window = sg.Window("Kereső", layout, finalize=True)
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
        if event == "PRODUCT_NO_DELETE" or event == "PRODUCT_NAME_DELETE":
            event = event.replace("_DELETE", '')
            self.window[event].Update("")
        if event == "Exit" or event == sg.WIN_CLOSED or event == "CANCEL":
            self.Close()
        elif event == "PRODUCT_NAME" or event == "PRODUCT_NO":
            res = core.search_for(core.PRODUCT, [values["PRODUCT_NO"], values["PRODUCT_NAME"]])
            if len(res) > 100: res = res[:100]
            self.window["PRODUCT_SHOW"].update(res)
        elif event == "PERSON" and values["PERSON"] != "":
            res = core.search_for(core.PERSON, values["PERSON"])
            if len(res) > 100: res = res[:100]
            self.window["PERSON_SHOW"].update(res)
        elif event == "PRODUCT_SHOW":
            if self.product_editor is not None and self.product_editor.is_running:
                self.product_editor.Close()
            if self.call_back is not None:
                self.product_editor = editor(values["PRODUCT_SHOW"][0], self.call_back, True, self.pre_set)
            else:
                self.product_editor = editor(values["PRODUCT_SHOW"][0], self.product_edited, False)
        elif event == "PERSON_SHOW":
            if self.call_back == None:
                if self.product_editor is not None and self.product_editor.is_running:
                    self.product_editor.Close()
                from note_lister import lister
                tmp = core.search_for([core.QUOTATION, core.DELIVERY_NOTE, core.ORDER], values["PERSON_SHOW"][0])
                if tmp == []:
                    sg.popup_auto_close("Nincs megjeleníthető adat", title="Figyelmeztetés")
                    return
                self.product_editor = lister(tmp, values["PERSON_SHOW"][0].name, None)
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
