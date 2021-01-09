import PySimpleGUI as sg
from data_structure import multiplyer

translator = None

class multi_selector:
    def __init__(self, call_back):
        global translator
        from core import translator
        self.call_back = call_back
        layout = [
            [sg.Text(translator.translate('ms_001')), sg.InputCombo(values=[multiplyer.MEGA, multiplyer.NAGYKER, multiplyer.SZERELO, multiplyer.KISKER], default_value=multiplyer.KISKER, key="SELECTOR"), sg.Button(button_text="Kész", key="FINISHED")]
        ]
        self.window = sg.Window(translator.translate('ms_002'), layout, return_keyboard_events=True)
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