import PySimpleGUI as sg
from data_structure import multiplyer

translator = None

class editor:
    def __init__(self, product, call_back, for_note=False, multi="Kisker"):
        """Allows the edit of a product, selected for either a note, or just viewing.
        """
        from core import translator
        self.is_running = True
        self.for_note = for_note
        self.product = product
        self.call_back = call_back
        self.multi = multi
        if for_note:
            layout = [
                [sg.Text(self.product.name)],
                [sg.Text(translator.translate('pe_001')), sg.In(default_text=self.product.inventory, key="AMOUNT", size=(10, 1)), sg.Text(translator.translate('ms_001')), sg.InputCombo(values=self.product.multiplyers, enable_events=True, key="MULTIPLYER", default_value=self.product.multiplyers.index(multi))],
                [sg.Text(translator.translate('pe_002')), sg.Text(f"{self.product.price*self.product.multiplyers[self.multi]:.2f}", key="PRICE"), sg.Text(translator.translate('pe_003')), sg.In(default_text="27", key="VAT", size=(4, 1))],
                [sg.Button(translator.translate('g_cancel'), key="CANCEL"), sg.Button(translator.translate('pe_004'), key="ADD")]
            ]
        else:
            mp = [[sg.Text(mpn), sg.In(default_text=mpv, key=mpn.upper())] for mpn, mpv in self.product.multiplyers.linking.items()]
            layout = [
                [sg.Text(translator.translate('ds_002')), sg.Text(self.product.no), sg.Text(translator.translate('ds_003')), sg.In(default_text=str(self.product.name or ""), key="PRODUCT_NAME")],
                [sg.Text(translator.translate('pe_001')), sg.In(default_text=self.product.inventory, key="INVENTORY"), sg.Text(translator.translate('pe_005')), sg.In(default_text=self.product.unit, key="UNIT")],
                [sg.Text(translator.translate('pe_002')), sg.In(default_text=self.product.price, key="PRICE")],
                [mp[0][0], mp[0][1], mp[1][0], mp[1][1]],
                [mp[2][0], mp[2][1], mp[3][0], mp[3][1]],
                [sg.Text(translator.translate('pe_006')), sg.In(default_text=self.product.max, key="MAX"), sg.Text(translator.translate('pe_007')), sg.In(default_text=self.product.min, key="MIN"), ],
                [sg.Button(translator.translate('g_cancel'), key="CANCEL"), sg.Button(translator.translate('g_save'), key="SAVE")]
            ]
        self.window = sg.Window(translator.translate('pe_008'), layout=layout, finalize=True, return_keyboard_events=True)
        self.read = self.window.read
    
    def work(self, event, values):
        if event == sg.WINDOW_CLOSED or event == "CANCEL" or event == "Escape:27":
            self.window.Close()
            self.is_running = False
        elif event == "MULTIPLYER":
            self.multi = values["MULTIPLYER"].split("-")[0]
            self.window["PRICE"].Update(f"{self.product.price*self.product.multiplyers[self.multi]:.2f}")
        elif event == "SAVE" or (event == '\r' and self.for_note):
            if self.product.name != values["PRODUCT_NAME"]:
                self.product.name = values["PRODUCT_NAME"]
            if self.product.inventory != int(values["INVENTORY"]):
                self.product.add_inventory(int(values["INVENTORY"]) - self.product.inventory, int(values["PRICE"]))
            if self.product.price != int(values["PRICE"]):
                self.product.price = int(values["PRICE"])
            tmp = multiplyer(values["MEGA"], values["NAGYKER"], values["SZERELŐ"], values["KISKER"])
            if self.product.multiplyers != tmp:
                self.product.multiplyers = tmp
            self.product.unit = values["UNIT"]
            self.product.max = int(values['MAX'])
            self.product.min = int(values['MIN'])
            self.call_back(self.product)
            self.is_running == False
            self.window.Close()
        elif event == "ADD" or (event == '\r' and not self.for_note):
            try:
                tmp = self.product.inherit(int(values["AMOUNT"]), values["MULTIPLYER"].split("-")[0], values["VAT"])
                self.call_back(tmp)
                self.is_running = False
                self.window.Close()
            except Exception as ex:
                sg.popup_error(f"{type(ex)} --> {ex}", title="Hiba")

    def Close(self):
        self.window.Close()
        self.is_running = False

    def show(self):
        while not self.window.was_closed():
            event, values = self.read(timeout=0)
            self.work(event, values)