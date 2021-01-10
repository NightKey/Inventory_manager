import json, os
#translations = {"Culture Codes": {"cc": "name"}, "key": {"cc": "value", "cc2": "value"}}
class translator:
    def __init__(self, culture_code):
        if not os.path.exists(os.path.join("translations", f"translations.json")):
            import urllib3
            response = urllib3.PoolManager().request("GET", "https://raw.githubusercontent.com/NightKey/Inventory_manager/master/translations/translations.json")
            if not os.path.exists("translations"):
                os.mkdir("translations")
            self.translations = json.loads(response.data, encoding="utf-8")
            with open(os.path.join("translations", f"translations.json"), "w", encoding="utf-8") as fp:
                json.dump(self.translations, fp)
        else:
            with open(os.path.join("translations", f"translations.json"), 'r', encoding="utf-8") as fp:
                self.translations = json.load(fp)
        self.culture_code = culture_code
    
    def translate(self, key):
        return self.translations[key][self.culture_code]

def get_avaleable_languages():
    with open(os.path.join("translations", f"translations.json"), 'r', encoding="utf-8") as fp:
        translations = json.load(fp)
    return translations["Culture Codes"]