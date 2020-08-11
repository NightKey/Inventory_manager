import PySimpleGUI as sg
from note_viewer import note_viewer

class from_note:
    def __init__(self, values, call_back):
        """shows the possible notes from the search, and sends back the selected one using the callback function.
        """
        self.is_running = True
        deliverynotes = [
            [sg.Text("Lehetséges adatok")],
            [sg.Listbox(values=values, enable_events=True, key="NOTE_SHOW", size=(75, 25))],
            [sg.Button("Kiválaszt", key="CREATE")]
        ]
        self.window = sg.Window("Szállító importálása", deliverynotes, finalize=True)
        self.call_back = call_back
        self.read = self.window.read
        self.nv = None

    def work(self, event, values):
        if event == "CREATE":
            self.call_back(values["NOTE_SHOW"][0])
            self.Close()
        elif event == sg.WINDOW_CLOSED:
            self.Close()
        elif event == "NOTE_SHOW":
            if self.nv is not None:
                self.nv.Close()
            self.nv = note_viewer(values["NOTE_SHOW"][0])
        if self.nv != None and self.nv.is_running:
            nevent, nvalues = self.nv.read(timeout=10)
            self.nv.work(nevent, nvalues)

    def Close(self):
        self.window.Close()
        if self.nv is not None and self.nv.is_running:
            self.nv.Close()
        self.is_running = False

    def show(self):
        while not self.window.was_closed():
            event, values = self.read(timeout=0)
            self.work(event, values)
            