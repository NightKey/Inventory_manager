import PySimpleGUI as sg
from product_editor import editor
from data_selector import selector
from data_structure import delivery_note
from multi_selector import multi_selector
from data_structure import product
import core, time
from datetime import datetime

class note_viewer:
    def __init__(self, note, _editor=False, product_call_back=None, call_back=None, _type=None):
        """Depending on the input data, shows a note or creates one, and either allows it to be edited, or allows it to be checked, and exported to invoice.
        """
        self.is_running = True
        self.note = note
        self.call_back = call_back
        self.product_call_back = product_call_back
        self.products = []
        self.person = None
        self.type = _type
        if self.note != None:
            layout = [
                [sg.Text("Személy"), sg.Text(self.note.person, size=(25, 1)), sg.Text("Megjegyzés"), sg.Text(self.note.note)],
                [sg.Listbox(values=self.note.products, size=(75, 25))],
                [sg.Button("Exportálás", key="EXPORT_NOTE"), sg.Button("Szerkesztés", key="EDIT"), sg.Text(text="Nettó:"), sg.Text(text="                 ", key="FINAL_PRICE_WOV"), sg.Text("Ft"), sg.Text(text="Végösszeg:"), sg.Text(text="                 ", key="FINAL_PRICE"), sg.Text("Ft")],
                [sg.Text("Létrehozva:"), sg.Text(str(datetime.fromtimestamp(self.note.creation)).split(".")[0])]
            ]
            editor = [
                [sg.Text("Személy"), sg.Text(self.note.person), sg.Button("Személy választása", key="PERSON_CHANGE"), sg.Text("Megjegyzés"), sg.Text(self.note.note)],
                [sg.Listbox(values=self.note.products, size=(120, 50), key="PRODUCT_EDIT", enable_events=True)], 
                [sg.Button("Új árucikk felvétele", key="NEW_PRODUCT"), sg.Button("Szerkesztés", key="EDIT_PRODUCT"), sg.Button("Törlés", key="DELETE_PRODUCT")],
                [sg.Button("Mégse", key="CANCEL"), sg.Button("Mentés", key="SAVE"), sg.Text(text="Végösszeg:"), sg.Text(text="                 ", key="FINAL_PRICE_WOV"), sg.Text("Ft"), sg.Text(text="Nettó:"), sg.Text(text="                 ", key="FINAL_PRICE"), sg.Text("Ft")]
            ]
        creator = [
            [sg.Text("Személy"), sg.Text(self.person, size=(25, 1), key="PERSON_SHOW"), sg.Button("Személy választása", key="PERSON_CHANGE"), sg.Text("Megjegyzés"), sg.In(key="NOTE")],
            [sg.Listbox(values=self.products, size=(120, 50), key="PRODUCT_EDIT", enable_events=True)], 
            [sg.Button("Új árucikk felvétele", key="NEW_PRODUCT"), sg.Button("Szerkesztés", key="EDIT_PRODUCT"), sg.Button("Törlés", key="DELETE_PRODUCT")],
            [sg.Button("Mégse", key="CANCEL"), sg.Button("Mentés", key="C_SAVE"), sg.Text(text="Nettó:"), sg.Text(text="                 ", key="FINAL_PRICE_WOV"), sg.Text("Ft"), sg.Text(text="Végösszeg:"), sg.Text(text="                 ", key="FINAL_PRICE"), sg.Text("Ft")]
        ]
        self.window = sg.Window((("Szállító" if self.note.type==3 else ("Rendelés" if self.note.type==4 else "Árajánlat")) if self.type == None else ("Szállító" if self.type==3 else ("Rendelés" if self.type==4 else "Árajánlat"))), layout=(editor if _editor else layout if _editor is not None else creator), finalize=True)
        self.read = self.window.read
        self.window.Finalize()
        self.product_editor = None
        self.searcher = None
        self.importer = None
        self.selected_value = None
        self.multi = "Kisker"
        self.update_final_prices()

    def update_final_prices(self):
        if self.note is not None:
            f = f"{sum([x.price*x.multiplyers[x.selected_multiplyer]*x.inventory for x in self.note.products.values()]):<8.0f}"
            fwv = f"{sum([x.price*x.multiplyers[x.selected_multiplyer]*x.inventory*(1+float(x.VAT)/100) for x in self.note.products.values()]):<8.0f}"
        else:
            f = f"{sum([x.price*x.multiplyers[x.selected_multiplyer]*x.inventory for x in self.products]):<8.0f}"
            fwv = f"{sum([x.price*x.multiplyers[x.selected_multiplyer]*x.inventory*(1+float(x.VAT)/100) for x in self.products]):<8.0f}"
        self.window["FINAL_PRICE_WOV"].Update(value=f)
        self.window["FINAL_PRICE"].Update(value=fwv)

    def person_changed(self, person):
        if self.type == None:
            self.note.change_person(person)
        else:
            self.person = person
            self.window["PERSON_SHOW"].Update(person)
            from from_note import from_note
            keys = [core.DELIVERY_NOTE if self.type <= core.DELIVERY_NOTE else None,
                    core.ORDER if self.type <= core.ORDER else None,
                    core.QUOTATION if self.type <= core.QUOTATION else None]
            try: keys.remove(None)
            except: pass
            if len(keys) == 1:
                keys = keys[0]
            elif len(keys) == 0:
                return
            possible = core.search_for(keys, person)
            if len(possible) > 0:
                self.importer = from_note(possible, self.import_from)
            else:
                sg.popup_auto_close(f"Nincs elmentett adat {person} személyhez!", title="Figyelmeztetés")
                self.importer = multi_selector(self.multi_selected)

    def import_from(self, item):
        if isinstance(item, delivery_note):
            self.products = list(core.append_deliverys(item))
        self.window["PRODUCT_EDIT"].Update(self.products)
        self.importer = multi_selector(self.multi_selected)
        self.update_final_prices()

    def product_happened(self, new_data):
        if self.selected_value == new_data and new_data is not None:
            if self.type == None:
                if self.note.type == core.DELIVERY_NOTE and core.products[core.products.index(new_data)].inventory <= new_data.inventory:
                    sg.popup_error(f"A '{new_data.name}' nevű árúból alig, vagy egyáltalán nincs elég a raktárban!\nFennmaradó mennyiség: {core.products[core.products.index(new_data)].inventory - new_data.inventory}", title="Raktár figyelmeztetés")
                self.product_call_back(self.note, self.selected_value, new_data)
            else:
                if self.type == core.DELIVERY_NOTE and core.products[core.products.index(new_data)].inventory <= new_data.inventory:
                    sg.popup_error(f"A '{new_data.name}' nevű árúból alig, vagy egyáltalán nincs elég a raktárban!\nFennmaradó mennyiség: {core.products[core.products.index(new_data)].inventory - new_data.inventory}", title="Raktár figyelmeztetés")
                self.products.remove(self.selected_value)
                self.products.append(new_data)
        elif new_data is None:
            if self.type == None:
                self.product_call_back(self.note, self.selected_value)
            else:
                self.products.remove(self.selected_value)
        elif self.selected_value != new_data:
            if self.type == None:
                if self.note.type == core.DELIVERY_NOTE and core.products[core.products.index(new_data)].inventory <= new_data.inventory:
                    sg.popup_error(f"A '{new_data.name}' nevű árúból alig, vagy egyáltalán nincs elég a raktárban!\nFennmaradó mennyiség: {core.products[core.products.index(new_data)].inventory - new_data.inventory}", title="Raktár figyelmeztetés")
                self.product_call_back(self.note, new_item=new_data)
            else:
                if self.type == core.DELIVERY_NOTE and core.products[core.products.index(new_data)].inventory <= new_data.inventory:
                    sg.popup_ok(f"A '{new_data.name}' nevű árúból alig, vagy egyáltalán nincs elég a raktárban!\nFennmaradó mennyiség: {core.products[core.products.index(new_data)].inventory - new_data.inventory}", title="Raktár figyelmeztetés")
                self.products.append(new_data)
        self.window["PRODUCT_EDIT"].Update(self.products)
        self.update_final_prices()

    def multi_selected(self, multi):
        self.multi = multi

    def work(self, event, values):
        if event == sg.WINDOW_CLOSED or event == "CANCEL":
            core.to_be_deleted = None
            self.Close()
            return
        elif event == "SAVE":
            core.delete_imported_note()
            self.Close()
            self.call_back(self.note)
            return
        elif event == "EDIT":
            self.Close()
            self.call_back.__self__.recall_in_editor(self.note)
        elif event == "PRODUCT_EDIT":
            self.selected_value = values["PRODUCT_EDIT"][0]
        elif event == "PERSON_CHANGE":
            self.searcher = selector(self.person_changed, selector.PERSON_SELECTOR)
        elif event == "NEW_PRODUCT":
            if self.product_editor is not None and self.product_editor.is_running:
                self.product_editor.Close()
            self.product_editor = selector(self.product_happened, selector.PRODUCT_SELECTOR, pre_set=self.multi)
        elif event == "EDIT_PRODUCT":
            if self.selected_value != None:
                if self.product_editor is not None and self.product_editor.is_running:
                    self.product_editor.Close()
                self.product_editor = editor(values["PRODUCT_EDIT"][0], self.product_happened, True, values["PRODUCT_EDIT"][0].selected_multiplyer)
        elif event == "DELETE_PRODUCT":
            if self.selected_value != None:
                self.product_happened(None)
        elif event == "EXPORT_NOTE":
            if self.note.type == core.DELIVERY_NOTE:
                self.note.export_to_invoice()
                core.save_everything(True)
                sg.popup_auto_close("Exportálva", title="Üzenet")
                self.call_back()
                self.Close()
            #else:
                
        elif event == "C_SAVE":
            self.Close()
            core.delete_imported_note()
            self.call_back(self.person, self.products, values["NOTE"] or None, self.type)
            return
        if self.searcher != None and self.searcher.is_running:
            sevent, svalues = self.searcher.read(timeout=10)
            self.searcher.work(sevent, svalues)
        if self.product_editor != None and self.product_editor.is_running:
            pevent, pvalues = self.product_editor.read(timeout=10)
            self.product_editor.work(pevent, pvalues)
        if self.importer != None and self.importer.is_running:
            ievent, ivalues = self.importer.read(timeout=10)
            self.importer.work(ievent, ivalues)
    
    def Close(self):
        self.is_running = False
        if self.product_editor is not None and self.product_editor.is_running:
            self.product_editor.Close()
        if self.searcher is not None and self.searcher.is_running:
            self.searcher.Close()
        if self.importer is not None and self.importer.is_running:
            self.importer.Close()
        self.window.Close()

    def timed(self, event, values):
        start = time.process_time()
        self.work(event, values)
        end = time.process_time()
        print(f"{event} took {end-start} s")

    def show(self):
        while self.is_running:
            event, values = self.read(timeout=0)
            self.timed(event, values)

if __name__=="__main__":
    from data_structure import delivery_note, person
    core.startup()
    p = person("0", "null", "")
    dn = delivery_note()
    dn.change_person(p)
    a = note_viewer(dn)
    a.show()
    b = note_viewer(dn, True)
    b.show()
    c = note_viewer(None, _editor=None, _type=core.QUOTATION)
    c.show()