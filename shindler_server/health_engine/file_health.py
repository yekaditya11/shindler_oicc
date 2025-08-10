import json
def file_health_fetch(id):
        with open(f"health_engine/srs{id}.health.json") as src_health_json:
            healt_data=json.load(src_health_json)

        return healt_data
    