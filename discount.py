import PySimpleGUI as sg
class discount:
    def __init__(self, items, call_back):
        layout = [
            [
                sg.In(default_text=0, size=(20,1), key="DISCOUNT", tooltip=r"A kedvezmény mértéke Ft-ban, vagy %-ban."),
                sg.Combo(values=["Ft", "\%"], default_value="Ft", key="SELECTOR"),
                sg.Button("Alkalmaz", key="APPLY")
            ]
        ]
        self.items = items
        self.window = sg.Window("Kedvezmény", layout, return_keyboard_events=True)
        self.is_running = True
        self.read = self.window.read
        self.total = 0
        self.call_back = call_back
        for item in self.items:
            self.total += item.price * item.multiplyers[item.selected_multiplyer]

    def Close(self):
        self.window.Close()
        self.is_running = False

    def work(self, event, values):
        if event == sg.WINDOW_CLOSED or event == "Escape:27":
            self.Close()
        elif event == "APPLY" or event == "\r":
            if values["SELECTOR"] == "Ft":
                ip = (int(values["DISCOUNT"])/self.total)*100    #INITIAL PERCENTAGE
            else:
                ip = int(values["DISCOUNT"])                                    #INITIAL PERCENTAGE
            dp = ip/len(self.items)                                             #DIRECT PERCENTAGE
            lst = []
            for item in self.items:
                if not item.check_discount(dp):
                    lst.append(item)
            if lst != []:
                lst = [f"\t{x}\n" for x in lst]
                tmp = "".join(lst)
                if sg.PopupYesNo(f"A következő termékek olcsóbbak lesznek, mint a beszerzési áruk:\n{tmp}\nAlkalmazza?", title="Ár riasztás") != "No":
                    self.call_back(dp, ip)
                    self.Close()
    
    def show(self):
        while self.is_running:
            event, values = self.read()
            self.work(event, values)