import PySimpleGUI as sg

class multi_selector:
    def __init__(self, call_back):
        self.call_back = call_back
        layout = [
            [sg.Text("Szorzó"), sg.InputCombo(values=["Mega", "Nagyker", "Szerelő", "Kisker"], default_value="Kisker", key="SELECTOR"), sg.Button(button_text="Kész", key="FINISHED")]
        ]
        self.window = sg.Window("Szorzó választó", layout, return_keyboard_events=True)
        self.read = self.window.read
        self.is_running = True

    def work(self, event, values):
        if event == sg.WINDOW_CLOSED:
            self.Close()
        elif event == "FINISHED" or event == "\r":
            self.call_back(values["SELECTOR"])
            self.Close()
        
    def Close(self):
        self.is_running = False
        self.window.Close()