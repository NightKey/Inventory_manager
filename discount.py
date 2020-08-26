import PySimpleGUI as sg
class discount:
    def __init__(self, initial, items, call_back):
        layout = [
            [
                sg.In(default_text=initial if initial is not None else 0, size=(20,1), key="DISCOUNT", tooltip=r"A kedvezmény mértéke Ft-ban, vagy %-ban."),
                sg.Combo(values=["Ft", r"%"], default_value=r"%" if initial is not None else r"%", key="SELECTOR"),
                sg.Button("Alkalmaz", key="APPLY")
            ]
        ]
        self.items = items
        self.window = sg.Window("Kedvezmény", layout, return_keyboard_events=True, finalize=True)
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
                if sg.PopupYesNo(f"A következő termékek olcsóbbak lesznek, mint a beszerzési áruk:\n{tmp}\nAlkalmazza?", title="Ár riasztás") != "No":
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
    if _type == "Ft":
        ip = (int(amount)/total)*100 #INITIAL PERCENTAGE
    else:
        ip = float(amount) #INITIAL PERCENTAGE
    return ip