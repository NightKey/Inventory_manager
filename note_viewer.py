import PySimpleGUI as sg
from product_editor import editor
from data_selector import selector
from data_structure import delivery_note
from multi_selector import multi_selector
from data_structure import product
from discount import discount, calculate
import core, time
from datetime import datetime

translator = None

class note_viewer:
    def __init__(self, note, _editor=False, product_call_back=None, call_back=None, _type=None):
        global translator
        from core import translator
        """Depending on the input data, shows a note or creates one, and either allows it to be edited, or allows it to be checked, and exported to invoice.
        """
        self.is_running = True
        self.note = note
        self.call_back = call_back
        self.product_call_back = product_call_back
        self.products = []
        self.person = None
        self.last_click = None
        self.type = _type
        if self.note != None:
            layout = [
                [sg.Text(translator.translate('nv_001')), sg.Text(self.note.person, size=(25, 1)), sg.Text(translator.translate('nv_002')), sg.Text(self.note.note)],
                [sg.Listbox(values=list(self.note.products.values()), size=(75, 25))],
                [
                    sg.Button(translator.translate('nv_003'), key="EXPORT_NOTE", disabled=self.note.locked),
                    sg.Button(translator.translate('nv_004'), key="EDIT", disabled=(self.note.locked or call_back is None)), sg.Text(text=f"{translator.translate('nv_005')}:"),
                    sg.Text(text="                 ", key="FINAL_PRICE_WOV"),
                    sg.Text(translator.translate('g_money_sign')), sg.Text(text=f"{translator.translate('nv_006')}:"), sg.Text(text="                 ", key="FINAL_PRICE"),
                    sg.Text(translator.translate('g_money_sign'))
                ],
                [sg.Text(f"{translator.translate('nv_007')}:"), sg.Text(str(datetime.fromtimestamp(self.note.creation)).split(".")[0]), sg.Text("ID:"), sg.Text(self.note.ID)]
            ]
            editor = [
                [sg.Text(translator.translate('nv_001')), sg.Text(self.note.person), sg.Button(translator.translate('nv_008'), key="PERSON_CHANGE"), sg.Text(translator.translate('nv_002')), sg.In(default_text=self.note.note, key="NOTE", enable_events=True)],
                [sg.Listbox(values=list(self.note.products.values()), size=(120, 35), key="PRODUCT_EDIT", enable_events=True, bind_return_key=True)], 
                [sg.Button(translator.translate('nv_009'), key="NEW_PRODUCT"), sg.Button(translator.translate('nv_010'), key="EDIT_PRODUCT"), sg.Button(translator.translate('nv_011'), key="DELETE_PRODUCT"), sg.Button(translator.translate('nv_012'), key="SET_DISCOUNT")],
                [
                    sg.Button(translator.translate('g_cancel'), key="CANCEL"),
                    sg.Button(translator.translate('g_save'), key="SAVE"),
                    sg.Text(text=f"{translator.translate('nv_006')}:"),
                    sg.Text(text="                 ", key="FINAL_PRICE_WOV"),
                    sg.Text(translator.translate('g_money_sign')),
                    sg.Text(text=f"{translator.translate('nv_005')}:"),
                    sg.Text(text="                 ", key="FINAL_PRICE"),
                    sg.Text(translator.translate('g_money_sign')),
                    sg.Text(f"{translator.translate('nv_013')}:"),
                    sg.Text("  0", key="DISCOUNT_VALUE"),
                    sg.Text("%")
                ]
            ]
        creator = [
            [sg.Text(translator.translate('nv_001')), sg.Text(self.person, size=(25, 1), key="PERSON_SHOW"), sg.Button(translator.translate('nv_008'), key="PERSON_CHANGE"), sg.Text(translator.translate('nv_002')), sg.In(key="NOTE")],
            [sg.Listbox(values=self.products, size=(120, 35), key="PRODUCT_EDIT", enable_events=True, bind_return_key=True)], 
            [sg.Button(translator.translate('nv_009'), key="NEW_PRODUCT"), sg.Button(translator.translate('nv_010'), key="EDIT_PRODUCT"), sg.Button(translator.translate('nv_011'), key="DELETE_PRODUCT"), sg.Button("Kedvezmény beállítása", key="SET_DISCOUNT")],
            [
                sg.Button(translator.translate('g_cancel'), key="CANCEL"),
                sg.Button(translator.translate('g_save'), key="C_SAVE"),
                sg.Text(text=f"{translator.translate('nv_006')}:"),
                sg.Text(text="                 ", key="FINAL_PRICE_WOV"),
                sg.Text(translator.translate('g_money_sign')),
                sg.Text(text=f"{translator.translate('nv_005')}:"),
                sg.Text(text="                 ", key="FINAL_PRICE"),
                sg.Text(translator.translate('g_money_sign')),
                sg.Text("  0", key="DISCOUNT_VALUE"),
                sg.Text("%")
            ]
        ]
        _type = self.note.type if self.type == None else self.type
        self.window = sg.Window((translator.translate('nv_014') if _type==3 else (translator.translate('nv_015') if _type==4 else translator.translate('nv_016'))), layout=(editor if _editor else layout if _editor is not None else creator), finalize=True, return_keyboard_events=True)
        self.read = self.window.read
        self.window.Finalize()
        self.product_editor = None
        self.searcher = None
        self.importer = None
        self.selected_value = None
        self.multi = "Kisker"
        self.update_final_prices()
        self.discount = 0 if note is None else note.discount
        if _editor or _editor is None:
            self.window["DISCOUNT_VALUE"].Update(f"{self.discount:3}")

    def update_final_prices(self):
        if self.note is not None:
            f = f"{self.note.get_total():<8.0f}"
            fwv = f"{self.note.get_total(True):<8.0f}"
        else:
            f = f"{sum([x.price*x.multiplyers[x.selected_multiplyer]*x.discount*x.inventory for x in self.products]):<8.0f}"
            fwv = f"{sum([x.price*x.multiplyers[x.selected_multiplyer]*x.discount*x.inventory*(1+float(x.VAT)/100) for x in self.products]):<8.0f}"
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
                sg.popup_auto_close(f"{translator.translate('nv_017')}: {person}!", title=translator.translate('g_alert'))
                self.importer = multi_selector(self.multi_selected)

    def get_discount_percentage(self, ip):
        self.window["DISCOUNT_VALUE"].Update(f"{ip:3}")
        self.discount = ip
        if self.note is not None:
            self.note.discount = ip
            for pr in self.note.products.values():
                pr.use_discount(ip)
                self.product_happened(pr, False)
        else:
            for pr in self.products:
                pr.use_discount(ip)
        self.update_final_prices()

    def import_from(self, item):
        if item is None or item == []:
            self.importer = multi_selector(self.multi_selected)
        else:
            self.ids = [x.ID for x in item]
            if len(item) > 1:
                for i in item:
                    self.products.extend(list(core.append_deliverys(i)))
            else:
                self.products.extend(list(core.append_deliverys(item[0])))
                self.window["NOTE"].Update(item[0].note)
                self.window["DISCOUNT_VALUE"].Update(item[0].discount)
            self.window["PRODUCT_EDIT"].Update(self.products)
            if item[0].multi is None:
                self.importer = multi_selector(self.multi_selected)
            else:
                self.multi = item[0].multi
            self.update_final_prices()

    def product_happened(self, new_data, check=True):
        if self.selected_value == new_data and new_data is not None:
            new_data.use_discount(self.discount)
            if self.type == None:
                if self.note.type == core.DELIVERY_NOTE and core.products[core.products.index(new_data)].inventory <= new_data.inventory and check:
                    sg.popup_error(f"{translator.translate('nv_018')} {new_data.name}!\n{translator.translate('nv_019')}: {core.products[core.products.index(new_data)].inventory - new_data.inventory}", title=translator.translate('g_alert'))
                self.note.edit_product(new_data)
            else:
                if self.type == core.DELIVERY_NOTE and core.products[core.products.index(new_data)].inventory <= new_data.inventory and check:
                    sg.popup_error(f"{translator.translate('nv_018')} {new_data.name}!\n{translator.translate('nv_019')}: {core.products[core.products.index(new_data)].inventory - new_data.inventory}", title=translator.translate('g_alert'))
                self.products.remove(self.selected_value)
                self.products.append(new_data)
        elif new_data is None:
            if self.type == None:
               self.note.remove_product(self.selected_value)
            else:
                self.products.remove(self.selected_value)
        elif self.selected_value != new_data:
            if self.type == None:
                if self.note.type == core.DELIVERY_NOTE and core.products[core.products.index(new_data)].inventory <= new_data.inventory and check:
                    sg.popup_error(f"{translator.translate('nv_018')} {new_data.name}!\n{translator.translate('nv_019')}: {core.products[core.products.index(new_data)].inventory - new_data.inventory}", title=translator.translate('g_alert'))
                self.note.add_product(new_data)
            else:
                if self.type == core.DELIVERY_NOTE and core.products[core.products.index(new_data)].inventory <= new_data.inventory and check:
                    sg.popup_error(f"{translator.translate('nv_018')} {new_data.name}!\n{translator.translate('nv_019')}: {core.products[core.products.index(new_data)].inventory - new_data.inventory}", title=translator.translate('g_alert'))
                self.products.append(new_data)
        if self.note is not None:
            calculate(self.note.discount, r'%', list(self.note.products.values()), self.note.get_total())
        self.window["PRODUCT_EDIT"].Update(self.products if (self.products != [] and self.note is None) else list(self.note.products.values()))
        self.update_final_prices()

    def multi_selected(self, multi):
        self.multi = multi

    def work(self, event, values):
        if event == sg.WINDOW_CLOSED or event == "CANCEL" or event == "Escape:27":
            core.to_be_deleted = None
            self.Close()
            return
        elif event == "SAVE":
            self.Close()
            self.call_back(self.note)
            return
        elif event == "EDIT":
            self.Close()
            self.call_back.__self__.recall_in_editor(self.note)
        elif event == "PRODUCT_EDIT":
            try:
                self.selected_value = values["PRODUCT_EDIT"][0]
            except: pass
        elif event == "PERSON_CHANGE":
            self.searcher = selector(self.person_changed, selector.PERSON_SELECTOR)
        elif event == "NEW_PRODUCT" or event=="Insert:45":
            if self.product_editor is not None and self.product_editor.is_running:
                self.product_editor.Close()
            self.product_editor = selector(self.product_happened, selector.PRODUCT_SELECTOR, pre_set=self.multi)
        elif event == "EDIT_PRODUCT" or event==" ":
            if self.selected_value != None:
                if self.product_editor is not None and self.product_editor.is_running:
                    self.product_editor.Close()
                self.product_editor = editor(values["PRODUCT_EDIT"][0], self.product_happened, True, multi=values["PRODUCT_EDIT"][0].selected_multiplyer)
        elif event == "DELETE_PRODUCT" or event == "Delete:46":
            if self.selected_value != None:
                self.product_happened(None)
        elif event == "EXPORT_NOTE":
            if self.note.locked == False:
                self.note.export_to_invoice()
                core.save_everything(True)
                sg.popup_auto_close("Exportálva", title="Üzenet")
                self.call_back()
                self.Close()
        elif event == "SET_DISCOUNT":
            if self.products == [] and (self.note is None or len(self.note.products) == 0):
                sg.PopupError(translator.translate('nv_020'))
                return
            if self.product_editor is not None:
                self.product_editor.Close()
            self.product_editor = discount(self.discount if self.discount != 0 else None, self.products if self.note is None else list(self.note.products.values()), self.get_discount_percentage)
        elif event == "Down:40":
            index = self.window["PRODUCT_EDIT"].GetIndexes()[-1] if self.window["PRODUCT_EDIT"].GetIndexes() != () else -1
            _max = len(self.products) if self.products != [] else len(self.note.products.values())
            self.window["PRODUCT_EDIT"].Update(scroll_to_index=index+1 if index < _max-1 else 0)
            self.window["PRODUCT_EDIT"].Update(set_to_index=index+1 if index < _max-1 else 0)
        elif event == "Up:38":
            index = self.window["PRODUCT_EDIT"].GetIndexes()[-1] if self.window["PRODUCT_EDIT"].GetIndexes() != () else -1
            _max = len(self.products) if self.products != [] else len(self.note.products.values())
            self.window["PRODUCT_EDIT"].Update(scroll_to_index=index+1 if index > 0 else _max-1)
            self.window["PRODUCT_EDIT"].Update(set_to_index=index+1 if index > 0 else _max-1)
        elif event == "NOTE":
            self.note.change_note(values["NOTE"])
        elif event == "C_SAVE":
            self.Close()
            ret = self.call_back(self.person, self.products, values["NOTE"] or None, self.type, self.multi)
            ret.discount = self.discount
            try:
                ret.created_from = self.ids
            except: pass
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
            event, values = self.read(timeout=10)
            self.work(event, values)

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