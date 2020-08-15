import PySimpleGUI as sg

class loading:
    def __init__(self):
        layout = [
            [sg.ProgressBar(5, orientation='h', size=(20, 20), key="BAR")]
        ]
        self.window = sg.Window("Loading", layout=layout, finalize=True, keep_on_top=True)
        self.read = self.window.read
        self.is_running = True
        self.bar = self.window.find_element("BAR")
    
    def Close(self):
        self.window.close()
        self.is_running = False

    def work(self, event, values):
        if event == sg.WINDOW_CLOSED:
            self.Close()
    
    def show(self):
        while self.is_running:
            e, v = self.read(timeout=10)
            self.work(e, v)

if __name__ == "__main__":
    a = loading()
    a.show()