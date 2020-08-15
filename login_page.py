import PySimpleGUI as sg

class login_page:
    def __init__(self):
        layout = [
            [sg.Text("Jelszó"), sg.In(key="PSW", password_char="*")],
            [sg.Button("Hitelesítés", key="VALIDATION")]
        ]
        self.window = sg.Window("Hitelesítés", layout=layout, finalize=True)
        self.read = self.window.read
        self.is_running = True

    def Close(self):
        self.window.Close()
        self.is_running = False

    def work(self, event, values):
        if event == "VALIDATION":
            self.Close()
            import core
            return core.settings.compare_password(values["PSW"])
        elif event == sg.WINDOW_CLOSED:
            self.Close()
            return False
    
    def show(self):
        while self.is_running:
            event, values = self.read()
            return self.work(event, values)