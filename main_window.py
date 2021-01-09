import PySimpleGUI as sg
import core, threading
from note_viewer import note_viewer
from note_lister import lister
from data_selector import selector
from setting_window import setting_window
from loading import loading

ld = loading()
ld.read(0)
data_correct = core.startup(bar=ld.bar, events=ld.events, hide=ld.hide, unhide=ld.unhide)
ld.Close()
translator = None

class main_window:
    def __init__(self):
        
        sg.theme("Dark")
        layout = [
            [sg.Button(translator.translate('mm_001'), key="NEW_DELIVERY", size=(12, 1)), sg.Button(translator.translate('mm_002'), key="NEW_ORDER", size=(12, 1)), sg.Button(translator.translate('mm_003'), key="NEW_QUOTATION", size=(12, 1))],
            [sg.Button(translator.translate('mm_004'), key="DELIVERYS", size=(12, 1)), sg.Button(translator.translate('mm_005'), key="ORDERS", size=(12, 1)), sg.Button(translator.translate('mm_006'), key="QUOTATIONS", size=(12, 1))],
            [sg.Button(translator.translate('mm_007'), key="PERSONS", size=(12, 1)), sg.Button(translator.translate('mm_008'), key="PRODUCTS", size=(12, 1)), sg.Button(translator.translate('mm_009'), key="SETTINGS", size=(12, 1), button_color=("White", "#0000FF"))],
            [sg.Button(translator.translate('mm_010'), key="SELF_ORDER", size=(17, 1)), sg.Button(translator.translate('mm_011'), key="NO_NAMED_PRODUCTS", size=(21, 1))],
            [sg.Button(translator.translate('mm_012'), key="HELP", size=(40, 1), button_color=("#000000", "#FFFFFF"))]
        ]
        self.window = sg.Window(title=translator.translate('mm_013'), layout=layout, return_keyboard_events=True)
        self.nc = None
        self.read = self.window.read
        self.is_running = True
        self.last_searched = None

    def re_search(self):
        if self.last_searched is not None:
            tmp = core.search_for(self.last_searched, None)
            if tmp == []:
                sg.popup_auto_close(translator.translate('mm_014'), title=translator.translate('g_alert'))
                return None
            else: return tmp

    def work(self, event):
            if event == sg.WINDOW_CLOSED or event == "Escape:27":
                self.Close()
            elif event == "F1:112" or event == "HELP":
                import webbrowser
                webbrowser.open('https://github.com/NightKey/Inventory_manager/blob/master/Help.MD', new=2)
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
                    sg.popup_auto_close(translator.translate('g_no_data'), title=translator.translate('g_alert'))
                else:
                    self.last_searched = core.DELIVERY_NOTE
                    if self.nc != None and self.nc.is_running:
                        self.nc.Close()
                    self.nc = lister(tmp, translator.translate('mm_004'), self.re_search)
            elif event == "ORDERS":
                tmp = core.search_for(core.ORDER, None)
                if tmp == []:
                    sg.popup_auto_close(translator.translate('g_no_data'), title=translator.translate('g_alert'))
                else:
                    self.last_searched = core.ORDER
                    if self.nc != None and self.nc.is_running:
                        self.nc.Close()
                    self.nc = lister(tmp, translator.translate('mm_005'), self.re_search)
            elif event == "QUOTATIONS":
                tmp = core.search_for(core.QUOTATION, None)
                if tmp == []:
                    sg.popup_auto_close(translator.translate('g_no_data'), title=translator.translate('g_alert'))
                else:
                    self.last_searched = core.QUOTATION
                    if self.nc != None and self.nc.is_running:
                        self.nc.Close()
                    self.nc = lister(tmp, translator.translate('mm_006'), self.re_search)
            elif event == "SELF_ORDER":
                core.self_order()
            elif event == "NO_NAMED_PRODUCTS":
                tmp = core.noname_items()
                if tmp != []:
                    if self.nc != None and self.nc.is_running:
                        self.nc.Close()
                    self.nc = selector(None, selector.NONAME_PRODUCTS, data=tmp)
                else:
                    sg.popup_auto_close(translator.translate('mm_017'), title=translator.translate('g_alert'))
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

from core import translator
if not data_correct[-1]:
    sg.popup_error(f"""{translator.translate('mm_014')}!\n
{translator.translate('mm_015')}\n{translator.translate('mm_016')}""", title=translator.translate('mm_017'))

to_start = main_window()
bg = threading.Thread(target=core.thread_checker)
bg.name = "Thread checker"
bg.start()
to_start.show()