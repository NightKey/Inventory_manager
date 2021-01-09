import PySimpleGUI as sg

translator = None

class discount:
    def __init__(self, initial, items, call_back):
        global translator
        from core import translator
        layout = [
            [
                sg.In(default_text=initial if initial is not None else 0, size=(20,1), key="DISCOUNT", tooltip=translator.translate('dis_001')),
                sg.Combo(values=[translator.translate('g_money_sign'), r"%"], default_value=r"%" if initial is not None else r"%", key="SELECTOR"),
                sg.Button(translator.translate('g_apply'), key="APPLY")
            ]
        ]
        self.items = items
        self.window = sg.Window(translator.translate('nv_013'), layout, return_keyboard_events=True, finalize=True)
        self.is_running = True
        self.read = self.window.read
        self.total = 0
        self.call_back = call_back
        for item in self.items:
            self.total += int(item.price * item.multiplyers[item.selected_multiplyer] * item.inventory)

    def Close(self):
        self.window.Close()
        self.is_running = False

    def work(self, event, values):
        if event == sg.WINDOW_CLOSED or event == "Escape:27":
            self.Close()
        elif event == "APPLY" or event == "\r":
            ip = calculate(values["DISCOUNT"], values["SELECTOR"], self.items, self.total)
            lst = []
            for item in self.items:
                if not item.check_discount(ip):
                    lst.append(item)
            if lst != []:
                lst = [f"\t{x}\n" for x in lst]
                tmp = "".join(lst)
                if sg.PopupYesNo(f"{translator.translate('dis_002')}\n{tmp}\n{translator.translate('dis_003')}?", title=translator.translate('dis_004')) != "No":
                    self.call_back(ip)
                    self.Close()
            else:
                self.call_back(ip)
                self.Close()
    
    def show(self):
        while self.is_running:
            event, values = self.read()
            self.work(event, values)

def calculate(amount, _type, items, total):
    """Calculates the percentage discount
    """
    if _type == translator.translate('g_money_sign'):
        ip = (int(amount)/total)*100 #INITIAL PERCENTAGE
    else:
        ip = float(amount) #INITIAL PERCENTAGE
    return ip