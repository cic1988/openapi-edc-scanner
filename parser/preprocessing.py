import json, os

class Preprocessor():
    def __init__(self, filepath, processingdir):
        self._filepath = filepath
        self._dir = processingdir

    def fix(self):
        with open(self._filepath) as f:
            # 1) null value not allowed for description field
            d = f.read().replace('"description": null', '"description": ""')
            d = d.replace('"description":null', '"description": ""')

            file_processed = self._dir + '/processed_' + os.path.basename(self._filepath)

            with open(file_processed, 'w') as processed:
                processed.write(d)
            
            return file_processed
