import PySimpleGUI as sg
class setting_window:
    def __init__(self):
        layout = [
            [sg.Text("Nyelv"), sg.Combo(values=["Magyar"], key="LANGUAGE")],
            [sg.Text("Újraimportálás jelszava"), sg.In(size=(25,1), password_char="*", tooltip="Min. 8 Character. Example: 'Th1S_1s_a_g00d_P@ssw0rd'", key="PSW")],
            #TODO Key binding settings
            [sg.Button("Mentés", key="SAVE")]
        ]
        self.window = sg.Window("Beállítások", layout=layout, finalize=True, keep_on_top=True)
        self.read = self.window.read
        self.is_running = True

    def Close(self):
        self.is_running = False
        self.window.Close()
    
    def work(self, event, values):
        if event == "SAVE":
            import core
            if not core.settings.set_password(values["PSW"]):
                sg.PopupOK("A jelszó nem megfelelő!\nKövetelmények:\n Min. 8 karakter\n Min 1 kicsi\n Minimum 1 nagy\n Minimum 1 szám\n Minimum 1 speciális (._-;,*+/~&@$)", title="Rossz Jelszó")
                return
            core.settings.set_language(values["LANGUAGE"])
            self.Close()
        elif event == sg.WINDOW_CLOSED:
            self.Close()
    
    def show(self):
        """It's a blocking show, so it can't be worked around!"""
        while self.is_running:
            event, values = self.read()
            self.work(event, values)