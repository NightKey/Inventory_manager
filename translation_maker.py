import os, json
#data = {"Culture Codes": {"cc": "name"}, "key": {"cc": "value", "cc2": "value"}}
with open(os.path.join("translations", "translations.json"), "r", encoding="utf-8") as fp:
    data = json.load(fp)

cc = input("Plesase type in the culture code (I.E.: en-US) of the lanugage: ")
if cc in data["Culture Codes"]:
    print("Culture code already exists!")
    input("Press return to exit")
    exit(0)
name = input("Please type in the name of the language (I.E.: US English): ")
data["Culture Codes"][cc] = name
for key, values in data.items():
    if key == "Culture Codes":
        continue
    values[cc] = input(f"{key} ({values['en-EN']}): ")

with open(os.path.join("translations", "translations.json"), "w", encoding="utf-8") as fp:
    json.dump(data, fp, ensure_ascii=False)