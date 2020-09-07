import PySimpleGUI as sg
from login_page import login_page
from loading import loading
class setting_window:
    def __init__(self):
        from core import settings
        sg.theme("Dark")
        layout = [
            [sg.Text("Importálási mappa helye", size=(35,1)), sg.FolderBrowse(button_text="...", initial_folder="./", key="IMPORT", enable_events=True, change_submits=True)],
            [sg.Text("Exportálási mappa helye", size=(35,1)), sg.FolderBrowse(button_text="...", initial_folder="./", key="EXPORT", enable_events=True)],
            [sg.Button("Újra importálás", key="REIMPORT", size=(12, 1), button_color=("White", "#FF0000"), disabled=(settings is None or settings.password is None))],
            [sg.Text("Újraimportálás jelszava", size=(20,1)), sg.In(size=(25,1), password_char="*", tooltip="Min. 8 karakter. Példa: '3z_3gy_Jó_J3lszó'", key="PSW")],
            [sg.Text("Előző jelszó" if settings is not None and settings.password is not None else "Jelszó ismét", size=(20,1)), sg.In(size=(25,1), password_char="*", key="PSW_")],
            [sg.Button("Mentés", key="SAVE", bind_return_key=True)]
        ]
        self.window = sg.Window("Beállítások", layout=layout, finalize=True, return_keyboard_events=True)
        self.read = self.window.read
        self.nc = None
        self.is_running = True
        self.initial = settings is None or settings.password is None

    def Close(self):
        self.is_running = False
        self.window.Close()
    
    def work(self, event, values):
        if event == "SAVE" or event == "\r":
            from core import settings
            if self.initial and values["PSW"] != values["PSW_"]:
                sg.PopupOK("A jelszavak nem egyeznek!", title="Rossz Jelszó")
                return
            elif not self.initial and not settings.compare_password(values["PSW_"]):
                sg.PopupOK("Az előző jelszó nem helyes!", title="Rossz Jelszó")
                return
            if not settings.set_password(values["PSW"]):
                sg.PopupOK("A jelszó nem megfelelő!\nKövetelmények:\n Min. 8 karakter\n Min 1 kicsi\n Minimum 1 nagy\n Minimum 1 szám\n Minimum 1 speciális (._-;,*+/~&@$)", title="Rossz Jelszó")
                return
            settings.set_destination(True, values["IMPORT"])
            settings.set_destination(False, values["EXPORT"])
            self.Close()
        elif event == "REIMPORT":
            import core
            if self.nc != None and self.nc.is_running:
                self.nc.Close()
            self.nc = login_page()
            ret = self.nc.show()
            if ret:
                self.nc = loading()
                core.startup(True, self.nc.bar, self.nc.events)
                self.nc.Close()
            elif ret is not None:
                sg.PopupOK("Hitelesítés sikertelen", title="Hitelesítés")
        elif event == sg.WINDOW_CLOSED or event == "Escape:27":
            self.Close()
    
    def show(self):
        """It's a blocking show, so it can't be worked around!"""
        while self.is_running:
            event, values = self.read()
            self.work(event, values)

if __name__=="__main__":
    stp = setting_window()
    stp.show()