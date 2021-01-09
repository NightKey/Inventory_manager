import PySimpleGUI as sg

class login_page:
    def __init__(self, compare_function):
        from core import translator
        layout = [
            [sg.Text(translator.translate('lg_001')), sg.In(key="PSW", password_char="*")],
            [sg.Button(translator.translate('lg_002'), key="VALIDATION", bind_return_key=True)]
        ]
        self.window = sg.Window(translator.translate('lg_002'), layout=layout, finalize=True, return_keyboard_events=True)
        self.read = self.window.read
        self.compare_function = compare_function
        self.is_running = True

    def Close(self):
        self.window.Close()
        self.is_running = False

    def work(self, event, values):
        if event == "VALIDATION" or event == "\r":
            self.Close()
            return self.compare_function(values["PSW"])
        elif event == sg.WINDOW_CLOSED or event == "Escape:27":
            self.Close()
            return None
    
    def show(self):
        while self.is_running:
            event, values = self.read()
            tmp = self.work(event, values)
        return tmp