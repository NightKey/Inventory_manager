from datetime import datetime
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
    def __init__(self, item_no, name, price=None, inventory=0, unit=None, _min=None, _max=None, multiplyers=multiplyer(1.0, 1.0, 1.0, 1.0), selected_multiplyer=None, VAT=None):
        self.no = item_no
        self.name = name
        self.inventory = inventory
        self.unit = unit
        self.price = price
        self.multiplyers = multiplyers
        self.VAT = VAT
        self.min=_min
        self.max=_max
        self.selected_multiplyer = selected_multiplyer
    
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

    def __rmul__(self, other):
        self.__mul__(other)

    def __hash__(self):
        return self.no.__hash__()

    def __repr__(self):
        return f"{self.no} - {self.inventory} {self.unit}"

    def __str__(self):
        if self.selected_multiplyer is not None: 
            pwm = self.price*self.multiplyers[self.selected_multiplyer]
            pwmm = pwm*self.inventory
            return f"{self.no:10.10}    {self.name:35.35}    {self.inventory} {self.unit}    {pwm:7.0f}    {pwmm:7.0f}"
        else: return f"{self.no} {self.name} {self.inventory}{self.unit} {self.price}"

class person:
    def __init__(self, code, name, cim):
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
    def __init__(self, note_type=DELIVERY):
        self.products = {}
        self.comment = ""
        self.locked = False
        self.type = note_type
        self.creation = datetime.now().timestamp()
    
    def change_person(self, person):
        if not self.locked:
            self.person = person
    
    def add_product(self, product):
        if not self.locked:
            try:
                self.products[product] = product
                return True
            except: pass
        return False
    
    def remove_product(self, product):
        if not self.locked:
            try:
                del self.products[product]
                return True
            except: pass
        return False

    def edit_product(self, new):
        if not self.locked:
            try:
                if not self.remove_product(new):
                    raise ValueError(f"The element '{new}'' was not in the products!")
                if not self.add_product(new):
                    raise ValueError(f"The element '{new}'' was not in the products!")
                return True
            except: pass
        return False

    def lock(self, key):
        if key == hash(self.person):
            self.locked = True

    def to_string(self):
        return (str(self.person), self.products)
    
    def extend(self, other):
        if not self.locked:
            if isinstance(other, delivery_note) and other.person == self.person:
                self.products.update(other.products)
                return True
            else:
                return False

    def __str__(self):
        return f'{"Szállító" if self.type==3 else "Rendelés" if self.type == 4 else "Árajánlat"} - {self.person} Létrehozva: {datetime.fromtimestamp(self.creation)}'
    
    def __repr__(self):
        return repr(self.products.keys())
    
    def __eq__(self, other):
        if isinstance(other, delivery_note):
            if self.person == other.person:
                if not self.locked and not other.locked:
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
            tmp = [[x.no, x.name, x.inventory, x.unit, x.price*x.multiplyers[x.selected_multiplyer], x.VAT] for x in self.products.values()]
            pd = ps.DataFrame(data=tmp)
            name = f"{self.person.name}-{str(datetime.now()).split(' ')[0]}.xlsx"
            pd.to_excel(os.path.join("exports", f"{name}"), index=False, header=False)
            while not os.path.exists(os.path.join("exports", f"{name}")): pass
            os.startfile(os.path.join("exports", f"{name}"))
            self.lock(hash(self.person))


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
    test_data()