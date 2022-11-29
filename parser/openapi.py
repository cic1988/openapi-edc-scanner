import copy
import logging

logger = logging.getLogger(__name__)

from prance import ResolvingParser
from model.model import OpenAPIModel

class OpenAPIParser():
    def __init__(self, endpoint, spec_string, dir, debug=False):
        parser = ResolvingParser(spec_string=spec_string)

        if debug:
            import json
            import os
            with open(os.path.join(dir, 'processed_' + endpoint), 'w') as fp:
                json.dump(parser.specification, fp)

        self._dir = dir
        self._model = OpenAPIModel()
        self._model.build(endpoint, parser.specification)
    
    def convert_objects(self, force=False):
        """ create objects.csv """
        import os
        assert os.path.exists(self._dir), "given dir not found: " + str(self._dir)

        if not force:
            assert os.path.exists(self._dir + '/objects.csv') == False, "objects.csv exists in: " + str(self._dir)
        else:
            import os
            import shutil

            for root, dirs, files in os.walk(self._dir):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))

        """ create tmp file """
        import csv
        import uuid
        import os

        tmp_file = os.path.abspath(self._dir) + '/objects.csv.' + uuid.uuid4().hex.upper()[0:6]

        with open(tmp_file, 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, self._model.object_csv_header.keys())
            writer.writeheader()

            if self._model.endpoint:
                writer.writerow(self._model.endpoint.build())
            
            if self._model.info:
                writer.writerow(self._model.info.build())

            if self._model.externalDocs:
                 writer.writerow(self._model.externalDocs.build())
            
            for schema in self._model.schemas:
                writer.writerow(schema.build())
            
            for prop in self._model.properties:
                writer.writerow(prop.build())
            
            for pathitem in self._model.paths:
                writer.writerow(pathitem.build())
            
            for operation in self._model.operations:
                writer.writerow(operation.build())

        if os.path.exists(tmp_file):
            os.rename(tmp_file, os.path.abspath(self._dir) + '/objects.csv')

    def convert_links(self, force=False):
        """ create links.csv """
        import os
        assert os.path.exists(self._dir), "given dir not found: " + str(self._dir)

        if not force:
            assert os.path.exists(self._dir + '/links.csv') == False, "links.csv exists in: " + str(self._dir)

        """ create tmp file """
        import csv
        import uuid
        import os
        import copy

        tmp_file = os.path.abspath(self._dir) + '/links.csv.' + uuid.uuid4().hex.upper()[0:6]

        with open(tmp_file, 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, self._model.link_csv_header.keys())
            writer.writeheader()

            for associationname, associationval in self._model.associations.items():
                for entry in associationval:
                    association = copy.deepcopy(self._model.link_csv_header)
                    association['association'] = associationname
                    association['fromObjectIdentity'] = entry['fromObjectIdentity']
                    association['toObjectIdentity'] = entry['toObjectIdentity']
                    writer.writerow(association)
         
        if os.path.exists(tmp_file):
            os.rename(tmp_file, os.path.abspath(self._dir) + '/links.csv')
    
    def zip_metadata(self):
        from zipfile import ZipFile
        zipMetadata = ZipFile(self._dir +  '/metadata.zip', 'w')

        import os
        from os.path import basename

        path = self._dir + '/objects.csv'

        if os.path.exists(path):
            zipMetadata.write(path, basename(path))
        
        path = self._dir + '/links.csv'
        
        if os.path.exists(path):
            zipMetadata.write(path, basename(path))
            return
        
        logger.info('[... zip objects.csv or links.csv failed ...]')
