import PySimpleGUI as sg
import core, threading
from note_viewer import note_viewer
from note_lister import lister
from data_selector import selector
from setting_window import setting_window

data_correct = core.startup()

class main_window:
    def __init__(self):
        sg.theme("Dark")
        layout = [
            [sg.Button("Új Szállító", key="NEW_DELIVERY", size=(12, 1)), sg.Button("Új Rendelés", key="NEW_ORDER", size=(12, 1)), sg.Button("Új Árajánlat", key="NEW_QUOTATION", size=(12, 1))],
            [sg.Button("Szállítók", key="DELIVERYS", size=(12, 1)), sg.Button("Rendelések", key="ORDERS", size=(12, 1)), sg.Button("Árajánlatok", key="QUOTATIONS", size=(12, 1))],
            [sg.Button("Személyek", key="PERSONS", size=(12, 1)), sg.Button("Árucikkek", key="PRODUCTS", size=(12, 1)), sg.Button("Beállítások", key="SETTINGS", size=(12, 1), button_color=("White", "#0000FF"))],
            [sg.Button("Autómatikus rendelés", key="SELF_ORDER", size=(17, 1)), sg.Button("Hibás árucikkek listázása", key="NO_NAMED_PRODUCTS", size=(21, 1))]
        ]
        self.window = sg.Window(title="Raktár kezelő", layout=layout, return_keyboard_events=True)
        self.nc = None
        self.read = self.window.read
        self.is_running = True
        self.last_searched = None

    def re_search(self):
        if self.last_searched is not None:
            tmp = core.search_for(self.last_searched, None)
            if tmp == []:
                sg.popup_auto_close("Nincs megjeleníthető szállító levél!", title="Figyelmeztetés")
                return None
            else: return tmp

    def work(self, event):
            if event == sg.WINDOW_CLOSED or event == "Escape:27":
                self.Close()
            elif event == "SETTINGS":
                if self.nc is not None and self.nc.is_running:
                    self.nc.Close()
                self.nc = setting_window()
            elif event == "PERSONS":
                if self.nc != None and self.nc.is_running:
                    self.nc.Close()
                self.nc = selector(None, _type=selector.PERSON_SELECTOR)
            elif event == "PRODUCTS":
                if self.nc != None and self.nc.is_running:
                    self.nc.Close()
                self.nc = selector(None, _type=selector.PRODUCT_SELECTOR)
            elif event == "NEW_DELIVERY":
                if self.nc != None and self.nc.is_running:
                    self.nc.Close()
                self.nc = note_viewer(None, _editor=None, product_call_back=None, call_back=core.create_delivery, _type=core.DELIVERY_NOTE)
            elif event == "NEW_ORDER":
                if self.nc != None and self.nc.is_running:
                    self.nc.Close()
                self.nc = note_viewer(None, _editor=None, product_call_back=None, call_back=core.create_delivery, _type=core.ORDER)
            elif event == "NEW_QUOTATION":
                if self.nc != None and self.nc.is_running:
                    self.nc.Close()
                self.nc = note_viewer(None, _editor=None, product_call_back=None, call_back=core.create_delivery, _type=core.QUOTATION)
            elif event == "DELIVERYS":
                tmp = core.search_for(core.DELIVERY_NOTE, None)
                if tmp == []:
                    sg.popup_auto_close("Nincs megjeleníthető szállító levél!", title="Figyelmeztetés")
                else:
                    self.last_searched = core.DELIVERY_NOTE
                    if self.nc != None and self.nc.is_running:
                        self.nc.Close()
                    self.nc = lister(tmp, "Szállítók", self.re_search)
            elif event == "ORDERS":
                tmp = core.search_for(core.ORDER, None)
                if tmp == []:
                    sg.popup_auto_close("Nincs megjeleníthető rendelés!", title="Figyelmeztetés")
                else:
                    self.last_searched = core.ORDER
                    if self.nc != None and self.nc.is_running:
                        self.nc.Close()
                    self.nc = lister(tmp, "Rendelések", self.re_search)
            elif event == "QUOTATIONS":
                tmp = core.search_for(core.QUOTATION, None)
                if tmp == []:
                    sg.popup_auto_close("Nincs megjeleníthető árajánlat!", title="Figyelmeztetés")
                else:
                    self.last_searched = core.QUOTATION
                    if self.nc != None and self.nc.is_running:
                        self.nc.Close()
                    self.nc = lister(tmp, "Árajánlatok", self.re_search)
            elif event == "SELF_ORDER":
                core.self_order()
            elif event == "NO_NAMED_PRODUCTS":
                tmp = core.noname_items()
                if tmp != []:
                    if self.nc != None and self.nc.is_running:
                        self.nc.Close()
                    self.nc = selector(None, selector.NONAME_PRODUCTS, data=tmp)
                else:
                    sg.popup_auto_close("Nem volt név nélküli árucikk", title="Figyelmeztetés")
            if self.nc != None and self.nc.is_running:
                nevent, nvalues = self.nc.read(timeout=10)
                self.nc.work(nevent, nvalues)
            elif self.nc != None:
                self.nc = None
    
    def Close(self):
        self.is_running = False
        if self.nc is not None and self.nc.is_running:
            self.nc.Close()
        core.save_everything()
        core.is_running = False
        self.window.Close()

    def show(self):
        while self.is_running:
            event, _ = self.read(timeout=12)
            self.work(event)

if not data_correct[-1]:
    sg.popup_error("""Az adatok nem voltak beolvashatóak, és az importáálás sikertelen volt!\n
Amennyiben a fileok jóhelyen vannak, győződjön meg a formátumok helyességéről!\nA mappák helyének megadásához használja a beállítások panelt!""", title="Adat hiba")

to_start = main_window()
bg = threading.Thread(target=core.thread_checker)
bg.name = "Thread checker"
bg.start()
to_start.show()