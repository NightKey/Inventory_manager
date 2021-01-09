import PySimpleGUI as sg
from login_page import login_page
from loading import loading

translator = None

class setting_window:
    def __init__(self):
        global translator
        from core import settings, translator
        import translate
        self.initial = settings is None or settings.password is None
        sg.theme("Dark")
        ln = translate.get_avaleable_languages()
        layout = [
            [sg.Text(translator.translate('sw_001'), size=(35,1)), sg.FolderBrowse(button_text="...", initial_folder="./", key="IMPORT", enable_events=True, change_submits=True)],
            [sg.Text(translator.translate('sw_002'), size=(35,1)), sg.FolderBrowse(button_text="...", initial_folder="./", key="EXPORT", enable_events=True)],
            [sg.Button(translator.translate('sw_003'), key="REIMPORT", size=(12, 1), button_color=("White", "#FF0000"), disabled=(settings is None or settings.password is None))],
            [sg.Text(translator.translate('sw_004'), size=(20,1)), sg.In(size=(25,1), password_char="*", tooltip=translator.translate('sw_005'), key="PSW")],
            [sg.Text(translator.translate('sw_006') if settings is not None and settings.password is not None else translator.translate('sw_007'), size=(20,1)), sg.In(size=(25,1), password_char="*", key="PSW_")],
            [sg.Text(translator.translate('sw_008'), size=(20,1)), sg.InputCombo(values=list(ln.values()), default_value=ln["hu-HU"] if self.initial else ln[settings.culture_code], size=(23, 1), tooltip=translator.translate('sw_009'), key="LANGUAGE", enable_events=True)],
            [sg.Button(translator.translate('g_save'), key="SAVE", bind_return_key=True)]
        ]
        self.window = sg.Window(translator.translate('sw_010'), layout=layout, finalize=True, return_keyboard_events=True)
        self.read = self.window.read
        self.nc = None
        self.is_running = True
        self.language_changed = False

    def Close(self):
        self.is_running = False
        self.window.Close()
    
    def work(self, event, values):
        if event == "SAVE" or event == "\r":
            from core import settings
            if self.initial and values["PSW"] != values["PSW_"]:
                sg.PopupOK(translator.translate('sw_013'), title=translator.translate('sw_012'))
                return
            elif not self.initial and values["PSW_"] != "" and values["PSW"] != "" and not settings.compare_password(values["PSW_"]):
                sg.PopupOK(translator.translate('sw_014'), title=translator.translate('sw_012'))
                return
            if values["PSW"] != "" and not settings.set_password(values["PSW"]):
                sg.PopupOK(f"{translator.translate('sw_015')}\n{translator.translate('sw_016')}\n {translator.translate('sw_017')}\n {translator.translate('sw_018')}\n {translator.translate('sw_019')}\n {translator.translate('sw_020')}\n {translator.translate('sw_021')} (._-;,*+/~&@$)", title=translator.translate("sw_012"))
                return
            settings.set_destination(True, values["IMPORT"])
            settings.set_destination(False, values["EXPORT"])
            settings.set_language(values["LANGUAGE"])
            import core
            core.save_settings()
            self.Close()
        elif event == "REIMPORT":
            import core
            if self.nc != None and self.nc.is_running:
                self.nc.Close()
            self.nc = login_page(core.settings.compare_password)
            ret = self.nc.show()
            if ret:
                self.nc = loading()
                core.startup(True, self.nc.bar, self.nc.events)
                self.nc.Close()
            elif ret is not None:
                sg.PopupOK(translator.translate("sw_022"), title=translator.translate("sw_023"))
        elif event == sg.WINDOW_CLOSED or event == "Escape:27":
            from core import settings
            if settings.password is None:
                sg.PopupOK(translator.translate('sw_011'), title=translator.translate('sw_012'))
            else:
                self.Close()
        elif event == "LANGUAGE":
            sg.popup_non_blocking(translator.translate("sw_024"), title=translator.translate("g_alert"))

    def show(self):
        """It's a blocking show, so it can't be worked around!"""
        while self.is_running:
            event, values = self.read()
            self.work(event, values)

if __name__=="__main__":
    stp = setting_window()
    stp.show()