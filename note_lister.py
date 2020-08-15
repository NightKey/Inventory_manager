import PySimpleGUI as sg
import core
from note_viewer import note_viewer

class lister:
    def __init__(self, data, name, call_back):
        """Lists out the notes. It wants a name and a list of notes. If a note is selected, calls the "Note viewer" with it.
        """
        layout = [
            [sg.Listbox(values=data, key="NOTE_SELECTOR", enable_events=True, size=(70, 25))]
        ]
        self.window = sg.Window(name, layout=layout, return_keyboard_events=True)
        self.read = self.window.read
        self.displayer = None
        self.is_running = True
        self.call_back = call_back
        self.selected_note = None
        self.check = True

    def finished(self):
        if self.call_back is None:
            return
        data = self.call_back()
        if data is None:
            self.Close()
        self.window["NOTE_SELECTOR"].Update(data)
    
    def finished_edit(self, note):
        core.save_note_changes(note, self.selected_note)
        self.selected_note = None
        core.save_everything(True)
        self.finished()

    def recall_in_editor(self, note):
        self.check = False
        self.displayer = note_viewer(note, _editor=True, product_call_back=core.edit_delivery_items, call_back=self.finished_edit)
        self.check = True

    def work(self, event, values):
        if event == "NOTE_SELECTOR":
            try:
                if self.displayer is not None and self.displayer.is_running:
                    self.displayer.Close()
                self.selected_note = values["NOTE_SELECTOR"][0]
                self.displayer = note_viewer(self.selected_note, call_back=self.finished)
            except: pass
        elif event == sg.WINDOW_CLOSED:
            self.is_running = False
            self.window.Close()
        if self.displayer is not None and self.displayer.is_running:
            devent, dvalues = self.displayer.read(timeout=10)
            self.displayer.work(devent, dvalues)
        elif self.displayer is not None and not self.displayer.is_running and self.check:
            self.displayer = None
    
    def Close(self):
        if self.displayer is not None and self.displayer.is_running:
            self.displayer.Close()
        self.is_running = False
        self.window.Close()
    
    def show(self):
        while not self.window.was_closed():
            event, values = self.read(timeout=10)
            self.work(event, values)