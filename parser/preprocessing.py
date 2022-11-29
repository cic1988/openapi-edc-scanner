import json, os

class Preprocessor():
    def __init__(self, filepath, processingdir):
        self._filepath = filepath
        self._dir = processingdir
    
    def fix(self):
        with open(self._filepath) as f:
            # 1) null value not allowed for description field
            return self.fix_null_description(f.read())
    
    def fix_null_description(self, str):
        str = str.replace('"description": null', '"description": ""')
        str = str.replace('"description":null', '"description": ""')
        return str


