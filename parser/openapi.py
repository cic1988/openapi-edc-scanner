import copy
import logging

logger = logging.getLogger(__name__)

from prance import ResolvingParser, BaseParser
from model.model import OpenAPIModel

class OpenAPIParser():
    def __init__(self, endpoint, filepath, dir):
        self._endpoint = endpoint
        self._info = 'Info'

        """ objects.csv / links.csv protocol """
        self._objects_head = {}
        self._links_head = {}
        self._model = OpenAPIModel()

        parser = ResolvingParser(filepath)
        self._spec = parser.specification
        self._dir = dir

        self._objects_head = {
            'class': '',
            'identity': '',
            'core.name': '',
            'core.description': ''
        }

        for attr, attrval in vars(self._model).items():
            if attr.startswith('_attr_'):
                self._objects_head[attrval] = ''

    def safe_get(self, keys, default=None):
        from functools import reduce
        return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), self._spec)
    
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
            writer = csv.DictWriter(f, self._objects_head.keys())
            writer.writeheader()
            self.convert_objects_endpoint(writer)
            self.convert_objects_info(writer)
            self.convert_objects_externalDocs(writer)
            self.convert_objects_schema(writer)
            self.convert_objects_pathitem(writer)

        if os.path.exists(tmp_file):
            os.rename(tmp_file, os.path.abspath(self._dir) + '/objects.csv')

    def convert_links(self, force=False):
        """ create links.csv """
        import os
        assert os.path.exists(self._dir), "given dir not found: " + str(self._dir)

        if not force:
            assert os.path.exists(self._dir + '/links.csv') == False, "links.csv exists in: " + str(self._dir)

        self._links_head = {
            'association': '',
            'fromObjectIdentity': '',
            'toObjectIdentity': ''
        }

        """ create tmp file """
        import csv
        import uuid
        import os
        import copy

        tmp_file = os.path.abspath(self._dir) + '/links.csv.' + uuid.uuid4().hex.upper()[0:6]

        with open(tmp_file, 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, self._links_head.keys())
            writer.writeheader()
            self.convert_links_resourceendpoint(writer)
            self.convert_links_endpointinfo(writer)
            self.convert_links_endpointschemaproperty(writer)
            self.convert_links_endpointpathitemoperation(writer)
         
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

    def convert_objects_endpoint(self, writer):
        endpoint = copy.deepcopy(self._objects_head)
        endpoint['class'] = self._model._class_endpoint
        endpoint['identity'] = self._endpoint
        endpoint['core.name'] = self._endpoint
        endpoint['core.description'] = self._endpoint
        writer.writerow(endpoint)
    
    def convert_objects_info(self, writer):
        deswithlinebreak = self.safe_get('info.description')
        if deswithlinebreak:
            deswithlinebreak = deswithlinebreak.replace('\n', '\\n')

        info = copy.deepcopy(self._objects_head)
        info['class'] = self._model._class_info
        info['identity'] = self._endpoint + '/' + self._info
        info['core.name'] = self._info
        info['core.description'] = deswithlinebreak
        info[self._model._attr_infocontactemail] = self.safe_get('info.contact.email')
        info[self._model._attr_infotitle] = self.safe_get('info.title')
        info[self._model._attr_infodescription] = deswithlinebreak
        info[self._model._attr_infotermsOfService] = self.safe_get('info.termsOfService')
        info[self._model._attr_infolicensename] = self.safe_get('info.license.name')
        info[self._model._attr_infoversion] = self.safe_get('info.version')
        writer.writerow(info)
    
    def convert_objects_externalDocs(self, writer):
        externalDocs = copy.deepcopy(self._objects_head)
        externalDocs['class'] = self._model._class_externaldocs
        externalDocs['core.name'] = 'externalDocs'
        externalDocs['identity'] = self._endpoint + '/' + externalDocs['core.name'] 
        externalDocs['core.description'] = self.safe_get('externalDocs.description')
        externalDocs[self._model._attr_externaldocs_url] = self.safe_get('externalDocs.url')
        writer.writerow(externalDocs)

    def convert_objects_schema(self, writer):
        schemas = self.safe_get('components.schemas')

        if not schemas:
            logger.warning('[WARNING] no schemas detected')
            return

        for schemaname, schemavalue in schemas.items():
            schema = copy.deepcopy(self._objects_head)
            schema['class'] = self._model._class_schema
            schema['core.name'] = schemaname
            schema['identity'] = self._endpoint + '/components/schemas/' + schema['core.name']
            schema['core.description'] = schema['identity']
            writer.writerow(schema)

            for propertyname, propertyvalue in schemavalue['properties'].items():
                prop = copy.deepcopy(self._objects_head)
                prop['class'] = self._model._class_property
                prop['core.name'] = propertyname
                prop['identity'] = schema['identity'] + '/' + prop['core.name']
                prop['core.description'] = propertyvalue.get('description')
                prop[self._model._attr_property_datatype] = propertyvalue.get('type')
                prop[self._model._attr_property_dataformat] = propertyvalue.get('format')
                prop[self._model._attr_property_example] = propertyvalue.get('example')
                writer.writerow(prop)
    
    def convert_objects_pathitem(self, writer):
        paths = self.safe_get('paths')

        if not paths:
            logger.warning('[WARNING] no paths detected')
            return
        
        for pathitemname, pathitemvalue in paths.items():
            pathitem = copy.deepcopy(self._objects_head)
            pathitem['class'] = self._model._class_pathitem
            pathitem['core.name'] = pathitemname.replace('/', '', 1)
            pathitem['identity'] = self._endpoint + '/paths/' + pathitem['core.name']
            pathitem['core.description'] = ''
            writer.writerow(pathitem)

            for operationname, operationvalue in pathitemvalue.items():
                operation = copy.deepcopy(self._objects_head)
                operation['class'] = self._model._class_operation
                operation['core.name'] = operationname
                operation['identity'] = pathitem['identity'] + '/' + operation['core.name']
                operation['core.description'] = operationvalue.get('description')
                writer.writerow(operation)
    
    def convert_links_resourceendpoint(self, writer):
        toplevel = copy.deepcopy(self._links_head)
        toplevel['association'] = self._model._association_resourceparanchild
        toplevel['toObjectIdentity'] = self._endpoint
        writer.writerow(toplevel)
    
    def convert_links_endpointinfo(self, writer):
        endpointinfo = copy.deepcopy(self._links_head)
        endpointinfo['association'] = self._model._association_endpointinfo
        endpointinfo['fromObjectIdentity'] = self._endpoint
        endpointinfo['toObjectIdentity'] = self._endpoint + '/' + self._info
        writer.writerow(endpointinfo)

    def convert_links_endpointschemaproperty(self, writer):
        schemas = self.safe_get('components.schemas')

        if not schemas:
            logger.warning('[WARNING] no schemas detected')
            return

        for schemaname, schemavalue in schemas.items():
            endpointschema = copy.deepcopy(self._links_head)
            endpointschema['association'] = self._model._association_enndpointschema
            endpointschema['fromObjectIdentity'] = self._endpoint
            endpointschema['toObjectIdentity'] = self._endpoint + '/components/schemas/' + schemaname
            writer.writerow(endpointschema)

            for propertyname, propertyvalue in schemavalue['properties'].items():
                schemaproperty = copy.deepcopy(self._links_head)
                schemaproperty['association'] = self._model._association_schemaproperty
                schemaproperty['fromObjectIdentity'] = endpointschema['toObjectIdentity']
                schemaproperty['toObjectIdentity'] = schemaproperty['fromObjectIdentity'] + '/' + propertyname
                writer.writerow(schemaproperty)

                if propertyvalue.get('type') == 'object':

                    try:
                        refs = list(schemas.keys())[list(schemas.values()).index(propertyvalue)]
                    except ValueError as ex:
                        if 'is not in list' in str(ex):
                            print(f'[EXCEPTION] object {propertyname} not available in schemas')
                            # TODO: recursive processing required
                            continue

                    if not refs:
                        logger.warning(f'[WARNING] referenced object {propertyname} not found in schemas')
                        continue

                    referenceschema = copy.deepcopy(self._links_head)
                    referenceschema['association'] = self._model._association_datasetdataflow
                    referenceschema['fromObjectIdentity'] = self._endpoint + '/components/schemas/' + refs
                    referenceschema['toObjectIdentity'] = schemaproperty['fromObjectIdentity']
                    writer.writerow(referenceschema)

                    referenceproperty = copy.deepcopy(self._links_head)
                    referenceproperty['association'] = self._model._association_directionaldataflow
                    # TODO: always link to id?
                    referenceproperty['fromObjectIdentity'] = referenceschema['fromObjectIdentity'] + '/id'
                    referenceproperty['toObjectIdentity'] = schemaproperty['toObjectIdentity']
                    writer.writerow(referenceproperty)
    
    def convert_links_endpointpathitemoperation(self, writer):
        paths = self.safe_get('paths')

        if not paths:
            logger.warning('[WARNING] no paths detected')
            return
        
        for pathitemname, pathitemvalue in paths.items():
            endpointpathitem = copy.deepcopy(self._links_head)
            endpointpathitem['association'] = self._model._association_endpointpathitem
            endpointpathitem['fromObjectIdentity'] = self._endpoint
            endpointpathitem['toObjectIdentity'] = self._endpoint + '/paths/' + pathitemname.replace('/', '', 1)
            writer.writerow(endpointpathitem)

            for operationname, operationvalue in pathitemvalue.items():
                pathitemoperation = copy.deepcopy(self._links_head)
                pathitemoperation['association'] = self._model._association_pathitemoperation
                pathitemoperation['fromObjectIdentity'] = endpointpathitem['toObjectIdentity'] 
                pathitemoperation['toObjectIdentity'] = pathitemoperation['fromObjectIdentity'] + '/' + operationname
                writer.writerow(pathitemoperation)

