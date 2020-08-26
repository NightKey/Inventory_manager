import PySimpleGUI as sg
import core
from note_viewer import note_viewer

class lister:
    def __init__(self, data, name, call_back):
        """Lists out the notes. It wants a name and a list of notes. If a note is selected, calls the "Note viewer" with it.
        """
        layout = [
            [sg.Listbox(values=data, key="NOTE_SELECTOR", enable_events=True, size=(70, 25), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED)],
            [sg.Button("Megtekintés", key="VIEW"), sg.Button("Összeolvasztás", key="MERGE", disabled=True)]
        ]
        self.data = data
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
        self.data = self.call_back()
        if self.data is None:
            self.Close()
        self.window["NOTE_SELECTOR"].Update(self.data)
    
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
            if len(values["NOTE_SELECTOR"]) > 1:
                self.window["MERGE"].Update(disabled=False)
                self.window["VIEW"].Update(disabled=True)
            else:
                self.window["MERGE"].Update(disabled=True)
                self.window["VIEW"].Update(disabled=False)
        elif event == "VIEW":
            try:
                if self.displayer is not None and self.displayer.is_running:
                    self.displayer.Close()
                self.selected_note = values["NOTE_SELECTOR"][-1]
                self.displayer = note_viewer(self.selected_note, call_back=self.finished)
                print(values["NOTE_SELECTOR"][-1])
            except: pass
        elif event == "MERGE":
            if self.displayer is not None and self.displayer.is_running:
                    self.displayer.Close()
            self.displayer = note_viewer(None, _editor=None, product_call_back=None, call_back=core.create_delivery, _type=values["NOTE_SELECTOR"][-1].type)
            self.displayer.import_from(values["NOTE_SELECTOR"])
        elif event == sg.WINDOW_CLOSED or event == "Escape:27":
            self.is_running = False
            self.window.Close()
        elif event == "Down:40":
            index = self.window["NOTE_SELECTOR"].GetIndexes()[-1] if self.window["NOTE_SELECTOR"].GetIndexes() != () else -1
            _max = len(self.data)
            self.window["NOTE_SELECTOR"].Update(scroll_to_index=index+1 if index < _max-1 else 0)
            self.window["NOTE_SELECTOR"].Update(set_to_index=index+1 if index < _max-1 else 0)
        elif event == "Up:38":
            index = self.window["NOTE_SELECTOR"].GetIndexes()[-1] if self.window["NOTE_SELECTOR"].GetIndexes() != () else -1
            _max = len(self.data)
            self.window["NOTE_SELECTOR"].Update(scroll_to_index=index+1 if index > 0 else _max-1)
            self.window["NOTE_SELECTOR"].Update(set_to_index=index+1 if index > 0 else _max-1)
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