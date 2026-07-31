import json, os
from ops import tally

products = json.load(open("data/products.json"))
api_key = os.environ.get("TALLY_API_KEY")
print("has key:", bool(api_key))
for p in products["products"]:
    try:
        intakes = tally.fetch_intakes(api_key, p["tally_form_id"])
        print(p["format"], len(intakes), "submissions")
        for i in intakes:
            print("  ", i["submission_id"], i["submitted_at"])
    except Exception as e:
        print(p["format"], "ERROR", repr(e))
