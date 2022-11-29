import json, os

class Preprocessor():
    def __init__(self, filepath, processingdir):
        self._filepath = filepath
        self._dir = processingdir
    
    def fix(self):
        with open(self._filepath) as f:
            # 1) null value not allowed for description field
            str_fix = self.fix_null_description(f.read())

            # 2) avoid endless loop
            return self.fix_endless_loop(str_fix)
    
    def fix_null_description(self, str):
        str = str.replace('"description": null', '"description": ""')
        str = str.replace('"description":null', '"description": ""')
        return str
    
    def fix_endless_loop(self, str):
        spec = json.loads(str)

        if 'components' in spec:
            schemas = spec['components']['schemas']

            if 'Extension' in schemas:
                val = schemas['Extension']

                if 'extension' in val['properties'] and 'items' in val['properties']['extension']:
                    ref = val['properties']['extension']['items']['$ref']

                    if ref == '#/components/schemas/Extension':
                        
                        spec['components']['schemas']['Extension']['properties']['extension']['items']['$ref'] = '#/components/schemas/Extension_ex'
                        spec['components']['schemas']['Extension_ex'] = {
                            'type': 'object',
                            'title': 'fake object to avoid Extension endless loop'
                        }
        return json.dumps(spec)


