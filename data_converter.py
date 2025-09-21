import json

class DataConverter:

    @staticmethod
    def to_json(articles):
        return json.dumps([article.__dict__ for article in articles], indent=2)