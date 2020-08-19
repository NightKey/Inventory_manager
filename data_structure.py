from datetime import datetime
from hashlib import sha256
import math
class setting:
    def __init__(self):
        self.language=None
        self.password=None
    
    def set_language(self, language):
        self.language = language
    
    def set_password(self, psw):
        if len(psw) > 7 and self.valid_password(psw):
            self.password = sha256(psw.encode("utf-8")).hexdigest()
            return True
        return False
    
    def compare_password(self, other):
        if not len(other) > 7 and self.valid_password(other):
            return False
        return self.password == sha256(other.encode("utf-8")).hexdigest()

    def valid_password(self, psw):
        import re
        lower="([a-z])+"
        upper = "([A-Z])+"
        num="([0-9])+"
        spec="([._\-;,*+/~&@$])+"
        return re.search(lower, psw) is not None and re.search(upper, psw) is not None and re.search(num, psw) is not None and re.search(spec, psw) is not None

class multiplyer:
    MEGA = "Mega"
    NAGYKER = "Nagyker"
    SZERELO = "Szerelő"
    KISKER = "Kisker"
    def __init__(self, Mega, Big, Mechanic, Small):
        self.linking = {"Mega":float(Mega), "Nagyker":float(Big), "Szerelő":float(Mechanic), "Kisker":float(Small)}
    
    def __getitem__(self, name):
        if name in self.linking: return self.linking[name]
        elif isinstance(name, int):
            if name < 4:
                keys = list(self.linking.keys())
                values = list(self.linking.values())
                return f"{keys[name]}-{values[name]}"
            else:
                raise StopIteration()
        else: return None
    
    def index(self, name):
        return f"{name}-{self[name]}"

    def __eq__(self, other):
        if isinstance(other, multiplyer):
            return self.linking == other.linking
        return False

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return 4

    def __str__(self):
        string = f""
        for x, y in self.linking.items():
            string += f"{x}-{y} "
        return  string[:-1]

    def __repr__(self):
        return [f"{x}-{y}" for x, y in self.linking.items()]

class product:
    def __init__(self, item_no, name, price=0, inventory=0, unit=None, _min=0, _max=0, multiplyers=multiplyer(1.0, 1.0, 1.0, 1.0), selected_multiplyer=None, VAT=None):
        self.no = item_no
        self.name = name
        self.inventory = int(inventory)
        self.unit = unit
        self.price = (int(price) if not math.isnan(price) else None)
        self.multiplyers = multiplyers
        self.VAT = VAT
        self.min=int(_min)
        self.max=int(_max)
        self.selected_multiplyer = selected_multiplyer
        self.discount = 1
    
    def add_inventory(self, amount, price=None):
        self.inventory += amount
        if price is not None:
            self.price = price

    def subtract_inventory(self, amount):
        self.inventory -= amount

    def inherit(self, amount, multiplyer, VAT=27):
        return product(self.no, self.name, self.price, amount,  self.unit, multiplyers=self.multiplyers, selected_multiplyer=multiplyer, VAT=VAT)

    def __eq__(self, other):
        if isinstance(other, product):
            return self.no == other.no
        else:
            return False

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self.price * other
        if isinstance(other, multiplyer):
            return self.price * other.amount
    
    def __contains__(self, item):
        """Item[0] - product_no, Item[1] - Product_name"""
        if isinstance(item, list):
            try: ret1 = item[0].lower() in self.no.lower()
            except: ret1 = False
            try: ret2 = item[1].lower() in self.name.lower()
            except: ret2 = False
            return ret1 and ret2

    def check_discount(self, discount):
        if self.price > self.price*self.multiplyers[self.selected_multiplyer]*float((100-discount)/100):
            return False
        return True
    
    def use_discount(self, discount):
        self.discount = float((100-discount)/100)

    def __rmul__(self, other):
        self.__mul__(other)

    def __hash__(self):
        return self.no.__hash__()

    def __repr__(self):
        return f"{self.no} - {self.inventory} {self.unit}"

    def __str__(self):
        if self.selected_multiplyer is not None: 
            pwm = self.price*self.multiplyers[self.selected_multiplyer]*self.discount
            pwmm = pwm*self.inventory
            return f"{self.no:10.10}    {self.name:35.35}    {self.inventory} {self.unit}    {pwm:7.0f}    {pwmm:7.0f}"
        else: return f"{self.no} {self.name} {self.inventory}{self.unit} {self.price}"

class person:
    def __init__(self, code, name, *cim):
        self.code = code
        self.name = name
        self.cim = cim

    def __eq__(self, other):
        if isinstance(other, (str, person)):
            return self.name == str(other)
        else:
            return False

    def __contains__(self, key):
        try: return key.lower() in self.name.lower()
        except: return False

    def __str__(self):
        return f"{self.name}"
    
    def __hash__(self):
        return self.code.__hash__()

class delivery_note:
    DELIVERY = 3
    ORDER = 4
    QUOTATION = 5
    def __init__(self, note_type=DELIVERY, note=None, ID=None, discount=[]):
        self.products = {}
        self.comment = ""
        self.locked = False
        ID = str(ID)
        self.ID = ID
        tmp = sha256(ID.encode("utf-8")).hexdigest()
        self.ID_Hash = tmp
        self.type = note_type
        self.note = note
        self.creation = datetime.now().timestamp()
        self.discount = discount
    
    def change_person(self, person):
        if not self.locked:
            self.person = person
            return True
        return None

    def add_product(self, product):
        if not self.locked:
            try:
                self.products[product] = product
                return True
            except: return False
        return None
    
    def change_note(self, new):
        if not self.locked:
            self.note = new
            return True
        return None

    def remove_product(self, product):
        if not self.locked:
            try:
                del self.products[product]
                return True
            except: return False
        return None

    def edit_product(self, new):
        if not self.locked:
            try:
                if not self.remove_product(new):
                    raise ValueError(f"The element '{new}'' was not in the products!")
                if not self.add_product(new):
                    raise ValueError(f"The element '{new}'' was not in the products!")
                return True
            except: return False
        return None

    def lock(self, key):
        if key == hash(self.person):
            self.locked = True
            return True
        return None

    def to_string(self):
        return (str(self.person), self.products)
    
    def extend(self, other):
        if not self.locked:
            if isinstance(other, delivery_note) and other.person == self.person:
                self.products.update(other.products)
                return True
            else:
                return False
        return None

    def __str__(self):
        return f'{"Szállító" if self.type==3 else "Rendelés" if self.type == 4 else "Árajánlat"} - {self.person} {f"Megjegyzés: {self.note}" if self.note is not None else ""} {"🔒" if self.locked else " "}'
    
    def __repr__(self):
        return repr(self.products.keys())
    
    def __eq__(self, other):
        if isinstance(other, delivery_note):
            if self.person == other.person:
                return self.products == other.products
        return False
    
    def __ne__(self, other):
        return not self == other

    def export_to_invoice(self):
        if not self.locked:
            import pandas as ps
            import os
            from datetime import datetime
            if not os.path.exists("exports"): os.mkdir("exports")
            tmp = [[x.no, x.name, x.inventory, x.unit, x.price*x.multiplyers[x.selected_multiplyer]*x.discount, x.VAT] for x in self.products.values()]
            pd = ps.DataFrame(data=tmp)
            name = f"{self.person.name}-{str(datetime.now()).split(' ')[0]}.xlsx"
            pd.to_excel(os.path.join("exports", f"{name}"), index=False, header=False)
            while not os.path.exists(os.path.join("exports", f"{name}")): pass
            os.startfile(os.path.join("exports", f"{name}"))
            self.lock(hash(self.person))
            return True
        return None


if __name__=="__main__":
    def test_data():
        p = person("xy", 'Gipsz', ["cím"])
        pr = product("CikkSzám1", "Cikk név",200, unit="DB")
        prr = product("CikkSzám2", "Cikk név",50, unit="CS")
        dn = delivery_note(delivery_note.DELIVERY)
        dn.change_person(p)
        dn.add_product(pr.inherit(10, 'Mega'))
        dn.add_product(prr.inherit(20, 'Nagyker'))
        _pr = pr.inherit(5, "Mega")
        dn.edit_product(_pr)
        print(dn.to_string())
        dn.export_to_invoice()
        setups = setting()
        print(f"not good password: {setups.set_password('NotGoodPassword')}")
        print(f"not long password: {setups.set_password('N0t_God')}")
        print(f"good password: {setups.set_password('1Ts_a_g00dP@ssw0rd')}")
    test_data()