import pickle
import threading
from copy import deepcopy
from datetime import datetime, timedelta
from os import mkdir, name, path, remove, system, walk
from time import sleep
import pandas as pd
from data_structure import person, product, delivery_note, setting, multiplyer

persons = []
products = []
delivery_notes = {"__ids__":[0,0,0,0]}
is_loading_data = False
loading_thread_counter = 0
threads = []
is_running = True
to_be_deleted = None
destination_saved='./data'
destination_import = "./import_from"
flags = {"person_read":False, "products_read":False, "delivery_read":True, "person_import":True, "products_import":True}
creating_thread = False
settings = None

#PRINT CLEAR - CONSOLE
def clear():
    system('cls' if name == "nt" else 'clear')

#FILE MANIPULATION SECTION - startup handdles these.
def read_data():
    global threads
    global loading_thread_counter
    for folder, _, files in walk(destination_saved):
        global creating_thread
        for file in files:
            creating_thread = True
            threads.append(threading.Thread(target=read_file, args=[folder, file]))
            threads[-1].name = folder
            threads[-1].start()
            creating_thread = False
    else:
        while True:
            counter = 0
            for t in threads:
                if t.is_alive():
                    counter += 1
            if loading_thread_counter != counter:
                loading_thread_counter = counter
            if counter == 0:
                break

def read_file(folder, file):
    global persons
    global products
    global delivery_notes
    with open(path.join(folder, file), 'br') as f:
        if file == 'persons.pc':
            try:
                persons = pickle.load(f)
                flags["person_read"] = True
            except EOFError:
                flags["person_import"] = False
                pass
        elif file == 'products.pc':
            try:
                products = pickle.load(f)
                flags["products_read"] = True
            except EOFError:
                flags["products_import"] = False
                pass
        elif file == 'delivery_notes.pc':
            try:
                flags["delivery_read"] = False
                delivery_notes = pickle.load(f)
                flags["delivery_read"] = True
            except EOFError:
                pass

def save_data(name, to_file):
    with open(path.join(destination_saved, f'{name}.pc'), 'bw') as f:
        pickle.dump(to_file, f)

def import_file(folder, file):
    global products
    global persons
    tmp = pd.read_excel(path.join(folder, file))
    if file == "Products.xlsx" and products == []:
        for collumn in tmp.values:
            mp = multiplyer(*collumn[7:])
            tmp = product(*collumn[:7], multiplyers=mp)
            products.append(tmp)
        save_data("products", products)
        flags["products_import"] = True
    elif file == "Persons.xlsx" and persons == []:
        for collumn in tmp.values:
            tmp = person(*collumn[:4])
            persons.append(tmp)
            flags["person_import"] = True

def save_everything(non_blocking=False):
    if non_blocking:
        global creating_thread
        for name, lst in [("persons", persons), ("products", products), ("delivery_notes", delivery_notes)]:
            creating_thread = True
            threads.append(threading.Thread(target=save_data, args=[name, lst,]))
            threads[-1].name = name
            threads[-1].start()
            creating_thread = False
    else:
        if persons != []:
            save_data("persons", persons)
        if products != []:
            save_data("products", products)
        if delivery_notes != {}:
            save_data("delivery_notes", delivery_notes)

def import_data(folder, bar=None, events=None):
    global is_loading_data
    global threads
    global loading_thread_counter
    for _, _, files in walk(folder):
        global creating_thread
        for file in files:
            if file == "VTSZ.xlsx":
                continue
            creating_thread = True
            threads.append(threading.Thread(target=import_file, args=[folder, file, ]))
            threads[-1].name = file
            threads[-1].start()
            creating_thread = False
        else:
            while True:
                counter = 0
                for t in threads:
                    if t.is_alive():
                        counter += 1
                if events is not None:
                        events.Update(f"{counter}/{len(threads)}")
                if loading_thread_counter != counter:
                    if not bar is None:
                        l = len(threads)
                        bar.UpdateBar(l-counter, l)
                    loading_thread_counter = counter
                if counter == 0:
                    break
            break
#FILE MANIPULATION SECTION END
#SETTINGS LOAD AND SAVE
def load_settings():
    global settings
    try:
        with open(path.join(destination_saved, "settings"), 'br') as f:
            settings = pickle.load(f)
    except:
        settings = setting()
        from setting_window import setting_window
        window = setting_window()
        window.show()
        save_settings()

def save_settings():
    with open(path.join(destination_saved, "settings"), 'bw') as f:
        pickle.dump(settings, f)
#SETTINGS LOAD AND SAVE END
#DATA MANIPULATION
PERSON = 0
PRODUCT = 1
DELIVERY_NOTE = 3
ORDER = 4
QUOTATION = 5
OUT_GOING = 6
def search_for(what, key):
    """Searches for the given data in the database.\n
    what - INT - core.PERSON|core.PROCUCT_NO|core.PRODUCT_NAME|core.DELIVERY_NOTE|core.ORDER|core.QUOTATION\n
    key - STR - Part of a person's/product's name, a part of a product's noumber.\n
    what - LIST - core.DELIVERY_NOTE|core.ORDER|core.QUOTATION\n
    key - NONE - For returning all deliverynotes with the 'what' type.\n
    """
    return_list = []
    if what == PERSON:
        for p in persons:
            try:
                if key.lower() in p.name.lower():
                    return_list.append(p)
            except: pass
    elif what == PRODUCT:
        for p in products:
            if key in p:
                return_list.append(p)
    elif what in [DELIVERY_NOTE, ORDER, QUOTATION] or DELIVERY_NOTE in what or ORDER in what or QUOTATION in what:
        if len(delivery_notes) > 1:
            if key != None and key in delivery_notes:
                for item in delivery_notes[key]:
                    try:
                        if isinstance(what, int):
                            if item.type == what:
                                return_list.append(item)
                        else:
                            if item.type in what:
                                return_list.append(item)
                    except: pass
            elif isinstance(key, str):
                for p, v in delivery_notes.items():
                    if p != "__ids__":
                        for note in v:
                            if not isinstance(note, int) and note.check_for_id(key):
                                return_list.append(note)
            elif key is None:
                for value in delivery_notes.values():
                    for item in value:
                        try:
                            if ((isinstance(what, (list, tuple)) and item.type in what) or item.type == what):
                                return_list.append(item)
                        except: pass
    return return_list

def append_deliverys(to_be_appended, append_to=None):
    """Appends two deliverynotes together, deleting the 'to_be_appended' from the database.\n
    Appending only works if neither of them is locked, and it's not the same one.\n
    append_to - DELIVERY NOTE - The delivery note to append to.\n
    to_be_appended - DELIVERY NOTE - The delivery note to be appended.\n
    """
    global to_be_deleted
    if append_to is None:
        to_be_deleted = to_be_appended
        save_everything(True)
        return list(to_be_appended.products.values())
    if append_to != to_be_appended and append_to.extend(to_be_appended) :
        to_be_deleted = to_be_appended
        save_everything(True)
        return True
    return False

def create_delivery(_person, item_list, note=None, _type=DELIVERY_NOTE, multi=None):
    """Creates a new deliverynote, with the selected type, and given itemlist, to the person's name.\n
    _person - PERSON - The person, who's name should be put on the deliverynote\n
    item_list - LIST - Values: the product as it should go to the deliverynote (multiplyer, VAT, amount)    \n
    _type - DELYVERY NOTE TYPE - A value that represents a note type core.DELIVERY_NOTE|core.ORDER|core.QUOTATION or delyvery_note.DELIVERY|delyvery_note.ORDER|delyvery_note.QUOTATION\n
    """
    id = delivery_notes["__ids__"][_type-3]
    tmp = delivery_note(_type if _type != OUT_GOING else DELIVERY_NOTE, note, id)
    delivery_notes["__ids__"][_type-3] += 1
    print(f"id: {id}, stored: {tmp.ID}")
    tmp.change_person(_person)
    for item in item_list:
        if _type == DELIVERY_NOTE:
            if persons.index(_person) == 0:
                products[products.index(item)].subtract_inventory(-1*item.inventory)
            else:
                products[products.index(item)].subtract_inventory(item.inventory)
        tmp.add_product(item)
    tmp.add_multi(multi)
    if _person in delivery_notes:
        delivery_notes[_person].append(tmp)
    else:    
        delivery_notes[_person] = [tmp]
    save_everything(True)
    return tmp

def save_note_changes(changed_note, old_note):
    """Saves the changed values for the note given.
    """
    for pr in old_note.products.values():
        edit_delivery_items(old_note, old_item=pr)
    delivery_notes[changed_note.person].remove(old_note)
    for pr in changed_note.products.values():
        edit_delivery_items(changed_note, new_item=pr)
    delivery_notes[changed_note.person].append(changed_note)

def delete_imported_note():
    """Deletes the imported note, when the new note was created by importing an existing one.
    """
    global to_be_deleted
    if to_be_deleted != None:
        tmp = tmp = delivery_notes[to_be_deleted.person]
        tmp.remove(to_be_deleted)
        to_be_deleted = None

def noname_items():
    """Returns a list of items, where all itmes have no names
    """
    tmp = []
    for pr in products:
        if isinstance(pr.name, float) or pr.price is None:
            tmp.append(pr)
    return tmp

def edit_delivery_items(note, old_item=None, new_item=None):
    """Edit's a delivery note item's item list.\n
    note - DELIVERY NOTE - The deliverynote to be edited.\n
    old_item - PRODUCT|NONE - The old state of the edited item, or None for adding new item.\n
    new_item - PRODUCT|NONE - The new state of the edited item, or None for removing old item\n
    Returns False, if wrong item was added, or both was None, else True
    """
    if new_item != None and old_item != None:
        if delivery_notes[note.person][delivery_notes[note.person].index(note)].edit_product(new_item):
            if note.type == DELIVERY_NOTE:
                products[products.index(old_item)].inventory += old_item.inventory - new_item.inventory
                save_everything(True)
            return True
    elif old_item != None and new_item == None:
        if delivery_notes[note.person][delivery_notes[note.person].index(note)].remove_product(old_item):
            if note.type == DELIVERY_NOTE:
                products[products.index(old_item)].inventory += old_item.inventory
                save_everything(True)
            return True
    elif old_item == None and new_item != None:
        if delivery_notes[note.person][delivery_notes[note.person].index(note)].add_product(new_item):
            if note.type == DELIVERY_NOTE:
                products[products.index(new_item)].inventory -= new_item.inventory
                save_everything(True)
            return True
    return False

def thread_checker():
    """Checks and destroys unalive threads from the 'threads' list
    """
    global is_running
    while is_running:
        for thread in threads:
            if not thread.is_alive() and not creating_thread:
                threads.remove(thread)
        sleep(0.2)

def self_order():
    """Creates a delivery note, and exports it to invoice, given the minimum and maximum amounts for each product
    """
    tmp = []
    for product in products:
        if product.min is not None and product.max is not None and product.inventory <= product.min and product.price is not None:
            tmp.append(product.inherit(product.max - product.inventory, "Mega"))
    if tmp == []:
        return
    so = create_delivery(persons[0], tmp, _type=OUT_GOING, note="Autómatikusan generált")
    from note_viewer import note_viewer
    t = note_viewer(so, True, edit_delivery_items, save_selforder_note)
    t.show()
    so.export_to_invoice()
    save_everything(True)

def save_selforder_note(note):
    pass

def startup(force_reimport=False, bar=None, events=None):
    """Reads in all data, then if needed, imports in everything and saves for future reads.\n
    Sets the 'is_loading_data' flag to true, while it's working.\n
    Returns the following list: [start, read_end, import_end, save_end, end, was_it_successfull]\n
    start - DATETIME - The starting time of the operation.\n
    read_end - DATETIME - The time the reading ended for the data previously saved.\n
    import_end - DATETIME|NONE - The time the import ended, if the import was needed, else it returns None.\n
    save_end - DATETIME|NONE - The time the save ended, if import was needed, else it returns None.\n
    was_it_successfull - boolean - True, if the loading was successfull
    """
    global is_loading_data
    global threads
    global persons
    global products
    global destination_saved
    global destination_import
    was_it_successfull = False
    if not force_reimport:
        load_settings()
        if settings.import_from is not None: destination_import = settings.import_from
        if not path.exists(destination_saved):
            mkdir(destination_saved)
        if not path.exists(destination_saved):
            mkdir(destination_saved)
        if not path.exists(destination_import):
            mkdir(destination_import)
    import_end = save_end = None
    is_loading_data = True
    start = datetime.now()
    if not force_reimport:
        read_data()
    else:
        persons = []
        products = []
    read_end = datetime.now()
    if (persons == [] or products == []) or force_reimport:
        threads = []
        import_data(destination_import, bar, events)
        import_end = datetime.now()
        persons.insert(0, person("*", "Duna ÉpületGépészeti Kft", "7100 Szekszárd, Sport u. 4."))
        save_everything()
        save_end = datetime.now()
    end = datetime.now()
    is_loading_data = False
    was_it_successfull = (sum(list(flags.values())) == 5)
    return [start, read_end, import_end, save_end, end, was_it_successfull]

if __name__=="__main__":
    #TEST FOR FUNCTIONALITY AND SPEED
    def _printer():
        char = "|"
        while printer_run:
            if is_loading_data:
                print(f"\rLoading {loading_thread_counter}/{len(threads)} {char}", end="")
                if char == "|":
                    char = "/"
                elif char == "/":
                    char = "-"
                elif char== "-":
                    char = "\\"
                else:
                    char = "|"
            sleep(0.2)
    
    global printer_run
    printer_run = True
    printer = threading.Thread(target=_printer)
    printer.name = "Printer Thread"
    printer.start()
    def import_test():
        print("Starting import test")
        global persons
        global products
        global is_loading_data
        global threads
        global loading_thread_counter
        global printer_run
        is_loading_data = True
        start = datetime.now()
        import_data(destination_import)
        import_end = datetime.now()
        import_time = import_end-start
        start = datetime.now()
        save_everything()
        save_end = datetime.now()
        save_time = save_end-start
        persons = []
        products = []
        loading_thread_counter = 0
        threads = []
        start = datetime.now()
        read_data()
        read_end = datetime.now()
        is_loading_data = False
        read_time = read_end-start
        printer_run = False
        print(f"\rImport finished in {import_time}")
        print(f"Save finished in {save_time}")
        print(f"Read finished in {read_time}")
    def functionality_test():
        print("Starting functionality test...")
        times = startup()
        txt = "Import needed" if times[2] != None and times[3] else None
        if txt != None:
            print(txt)
        print(f"Startup finished under {times[-1] - times[0]}")
        p = persons[0]
        print("Delivery creation")
        print(f"{products[0]}: {products[0].inventory}")
        itemlist = [x.inherit(10, multiplyer.MEGA, 28) for x in products[:5]]
        dn = create_delivery(p, itemlist, delivery_note.ORDER)
        print(f"{products[0]}: {products[0].inventory}")
        print(f"Empty: {edit_delivery_items(dn)}")
        print(f"Add: {edit_delivery_items(dn, new_item=products[5].inherit(5, multiplyer.KISKER, 25))}")
        print(f"DN: {search_for(ORDER, p)}")
        print(f"Remove: {edit_delivery_items(dn, old_item=products[1])}")
        print(f"DN: {search_for(ORDER, p)}")
        print(f"Edit: {edit_delivery_items(dn, products[5].inherit(5, multiplyer.KISKER, 25), products[5].inherit(20, multiplyer.KISKER, 25))}")
        print(f"DN: {search_for(ORDER, p)}")
        dn.export_to_invoice()
        print(f"DN: {search_for(ORDER, p)}")
    def search_test():
        print("Starting search speed test")
        times = startup()
        print(f"Data loaded under {times[-1] - times[0]}")
        import time
        start = time.process_time()
        search_for(PERSON, "a")
        a = time.process_time()
        search_for(PERSON, "asd")
        asd = time.process_time()
        print(f"Searching for 'a' in the 'persons' list took {a-start} s")
        print(f"Searching for 'asd' in the 'persons' list took {asd-a} s")
        print(f"The total operation took {asd-start} s")
    ch = input("1 - import_test\n2 - functionality_test\n3 - search timer\n:")
    if ch == '1':
        import_test()
    elif ch == '2':
        functionality_test()
    elif ch == '3':
        search_test()
    printer_run = False
    input("Press enter to exit...")
