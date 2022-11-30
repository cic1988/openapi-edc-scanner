import copy
import json
import logging
logger = logging.getLogger(__name__)

class OpenAPIModel():
    def __init__(self):
        """
        see model/model.xml
        """

        self._objects_head = {}
        self._links_head = {
            'association': '',
            'fromObjectIdentity': '',
            'toObjectIdentity': ''
        }
        self._packagename = OpenAPIModel.packagename()

        """ association """
        self._association_resourceparanchild = 'core.ResourceParentChild'
        self._association_endpointinfo = self._packagename + '.endpointinfo'
        self._association_enndpointschema = self._packagename + '.endpointschema'
        self._association_schemaproperty = self._packagename + '.schemaproperty'
        self._association_schemaschema = self._packagename + '.schemaschema'
        self._association_endpointpathitem = self._packagename + '.endpointpath'
        self._association_pathitemoperation = self._packagename + '.pathoperation'

        """ lineage (within the data source) """
        self._association_datasourcedataflow = 'core.DataSourceDataFlow'
        self._association_datasetdataflow = 'core.DataSetDataFlow'
        self._association_directionaldataflow = 'core.DirectionalDataFlow'

        self._spec = None
        self._endpoint = None
        self._info = None
        self._externaldocs = None
        self._schemas = []
        self._properties = []
        self._paths = []
        self._operations = []

        self._associations = {
            self._association_resourceparanchild: [],
            self._association_endpointinfo: [],
            self._association_enndpointschema: [],
            self._association_schemaproperty: [],
            self._association_schemaschema: [],
            self._association_endpointpathitem: [],
            self._association_pathitemoperation: []
        }
    
    @staticmethod
    def packagename():
        return 'com.informatica.ldm.openapi'
    
    @property
    def object_csv_header(self):
        return self._objects_head

    @property
    def link_csv_header(self):
        return self._links_head
    
    @property
    def associations(self):
        return self._associations
    
    @property
    def endpoint(self):
        return self._endpoint
    
    @property
    def info(self):
        return self._info
    
    @property
    def externalDocs(self):
        return self._externaldocs
    
    @property
    def schemas(self):
        return self._schemas
    
    @property
    def properties(self):
        return self._properties
    
    @property
    def paths(self):
        return self._paths
    
    @property
    def operations(self):
        return self._operations
    
    def build_schema(self, schema):
        self._schemas.append(schema)
        schemachildren = schema.children()

        for child in schemachildren:
            if type(child) == Schema:
                self.build_schema(child)

                self._associations[self._association_schemaschema].append({
                    'fromObjectIdentity': schema.id,
                    'toObjectIdentity': child.id
                })
            elif type(child) == SchemaProperty:
                self._properties.append(child)

                self._associations[self._association_schemaproperty].append({
                    'fromObjectIdentity': schema.id,
                    'toObjectIdentity': child.id
                })
            else:
                logger.warning(f'[WARNING] unknown type of {child.path} detected')

    def build(self, endpoint, spec):
        self._spec = spec
        self._endpoint = Endpoint(endpoint, endpoint, self._spec)
        self._associations[self._association_resourceparanchild].append({
            'fromObjectIdentity': '',
            'toObjectIdentity': self._endpoint.id
        })

        self._info = Info(endpoint+ '/Info', 'Info', self._spec)
        self._associations[self._association_endpointinfo].append({
            'fromObjectIdentity': self._endpoint.id,
            'toObjectIdentity': self._info.id
        })

        self._externaldocs = ExternalDocs(endpoint + '/' + 'externalDocs', 'externalDocs', self._spec)        
        self._objects_head = self._endpoint._objects_head

        toplevelschemas = self.safe_get('components.schemas', self._spec)
        for schemaname, schemavalue in toplevelschemas.items():
            # TODO: if the toplevel already has schema array?
            schema = Schema(endpoint + '/components/schemas/' + schemaname, schemaname, self._spec)
            self.build_schema(schema)

            self._associations[self._association_enndpointschema].append({
                'fromObjectIdentity': self._endpoint.id,
                'toObjectIdentity': schema.id
            })
        
        paths = self.safe_get('paths', self._spec)

        for pathitemname, pathitemvalue in paths.items():
            pathitem = PathItem(endpoint + '/paths/' + pathitemname, pathitemname, self._spec)
            self._paths.append(pathitem)
            self._operations.extend(pathitem.operations())

            self._associations[self._association_endpointpathitem].append({
                'fromObjectIdentity': self._endpoint.id,
                'toObjectIdentity': pathitem.id
            })
        
            for operation in pathitem.operations():
                self._associations[self._association_pathitemoperation].append({
                    'fromObjectIdentity': pathitem.id,
                    'toObjectIdentity': operation.id
                })
    
    @staticmethod
    def safe_get(keys, spec, default=None):
        from functools import reduce
        return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), spec)

class Identifier():
    def __init__(self, id, name, description=None, spec=None):
        self._packagename = OpenAPIModel.packagename()
        self._classname = ''
        self._id = id
        self._path = ''
        self._ref = ''
        self._name = name
        self._description = description
        self._spec = spec

        """ 1) model attribute """
        self._attr_endpoint_version = self._packagename + '.openapi'
        self._attr_infoversion = self._packagename + '.infoversion'
        self._attr_infotitle = self._packagename + '.infotitle'
        self._attr_infodescription = self._packagename + '.infodescription'
        self._attr_infotermsOfService = self._packagename + '.infotermsOfService'
        self._attr_infocontactemail = self._packagename + '.infocontactemail'
        self._attr_infolicensename = self._packagename + '.infolicensename'
        self._attr_externaldocs_url = self._packagename + '.externaldocsurl'
        self._attr_property_example = self._packagename + '.propertyexample'
        self._attr_isarray = self._packagename + '.schemapropertyarray'

        """ 2) base attribute (inherited from base model) """
        self._attr_property_primarykey = 'com.infa.ldm.relational.PrimaryKeyColumn'
        self._attr_property_datatype = 'com.infa.ldm.relational.Datatype'
        self._attr_property_dataformat = 'com.infa.ldm.relational.FieldFormat'
        self._attr_property_nullable = 'com.infa.ldm.relational.Nullable'
        self._attr_property_maxlength = 'com.infa.ldm.relational.DatatypeLength'
        self._attr_property_scale = 'com.infa.ldm.relational.DatatypeScale'

        self._objects_head = {
            'class': '',
            'identity': '',
            'core.name': '',
            'core.description': ''
        }

        for attr, attrval in vars(self).items():
            if attr.startswith('_attr_'):
                self._objects_head[attrval] = ''
    
    @property
    def classname(self):
        return self._classname

    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def spec(self):
        return self._spec
    
    @property
    def path(self):
        return self._path

    @property
    def reference(self):
        return self._ref

    def build(self):
        pass

class Endpoint(Identifier):
    def __init__(self, name, description=None, spec=None):
        super(Endpoint, self).__init__(name, name, description, spec)
        self._classname = self._packagename + '.endpoint'
    
    @property
    def version(self):
        return OpenAPIModel.safe_get('openapi', self._spec)
    
    def build(self):
        endpoint = copy.deepcopy(self._objects_head)
        endpoint['class'] = self.classname
        endpoint['identity'] = self.id
        endpoint['core.name'] = self.name
        endpoint['core.description'] = self.description
        endpoint[self._attr_endpoint_version] = self.version
        return endpoint

class Info(Identifier):
    def __init__(self, id, name, spec):
        super(Info, self).__init__(id, name, '', spec)
        self._classname = self._packagename + '.info'
        deswithlinebreak = OpenAPIModel.safe_get('info.description', self._spec)

        if deswithlinebreak:
            self._description = deswithlinebreak.replace('\n', '\\n')
    
    @property
    def contactemail(self):
        return OpenAPIModel.safe_get('info.contact.email', self._spec)
    
    @property
    def title(self):
        return OpenAPIModel.safe_get('info.title', self._spec)

    @property
    def termsOfService(self):
        return OpenAPIModel.safe_get('info.termsOfService', self._spec)

    @property
    def licensename(self):
        return OpenAPIModel.safe_get('info.license.name', self._spec)

    @property
    def version(self):
        return OpenAPIModel.safe_get('info.version', self._spec)

    def build(self):
        super(Info, self).build()
        info = copy.deepcopy(self._objects_head)
        info['class'] = self.classname
        info['identity'] = self.id
        info['core.name'] = self.name
        info['core.description'] = self.description
        info[self._attr_infocontactemail] = self.contactemail
        info[self._attr_infotitle] = self.title
        info[self._attr_infotermsOfService] = self.termsOfService
        info[self._attr_infolicensename] = self.licensename
        info[self._attr_infoversion] = self.version
        return info

class ExternalDocs(Identifier):
    def __init__(self, id, name, spec):
        super(ExternalDocs, self).__init__(id, name, '', spec)
        self._classname = self._packagename + '.externaldocs'
        self._description = OpenAPIModel.safe_get('externalDocs.description', self._spec)
    
    @property
    def url(self):
        return OpenAPIModel.safe_get('externalDocs.url', self._spec)
    
    def build(self):
        super(ExternalDocs, self).build()
        externalDocs = copy.deepcopy(self._objects_head)
        externalDocs['class'] = self.classname
        externalDocs['core.name'] = self.name
        externalDocs['identity'] = self.id
        externalDocs['core.description'] = self.description
        externalDocs[self._attr_externaldocs_url] = self.url
        return externalDocs

class Schema(Identifier):
    def __init__(self, id, name, spec):
        super(Schema, self).__init__(id, name, '', spec)
        self._classname = self._packagename + '.schema'
        # TODO: schema description for 3.0.x
        self._description = ''
        self._children_initialized = False
        self._children = []
        self._isarray = False
        self._example = ''

        import re
        regex = 'components\/schemas\/\S+'
        matches = re.finditer(regex, self.id)

        for match in matches:
            self._path = match.group(0)
            break

        key = self.path.replace('/', '.')
        self._schemavalue = OpenAPIModel.safe_get(key, self.spec)

    @property
    def schemavalue(self):
        return self._schemavalue
    
    @property
    def description(self):
        if super(Schema, self).description:
            return super(Schema, self).description
        
        if self.schemavalue:
            return OpenAPIModel.safe_get('description', self.schemavalue)

        return ''
    
    @property
    def isarray(self):
        return self._isarray
    
    def build(self):
        schema = copy.deepcopy(self._objects_head)
        schema['class'] = self.classname
        schema['core.name'] = self.name
        schema['identity'] = self.id
        schema['core.description'] = self.description
        schema[self._attr_isarray] = self.isarray
        schema[self._attr_property_example] = self._example
        return schema
    
    # children could be property or schema
    def children(self):
        if self._children_initialized:
            return self._children
        
        if not self.schemavalue:
            logger.warning(f'[WARNING] Schema {self.path} without schema value')
            self._children_initialized = True
            return self._children

        properties = None
        # handle inheritage:
        # 1) 'allOf':
        if 'allOf' in self.schemavalue:
            properties = dict()

            for block in self.schemavalue['allOf']:
                additional_properties = block.get('properties')

                if additional_properties:
                    properties.update(additional_properties)

        else:
            properties = self.schemavalue.get('properties')

        if not properties:
            logger.warning(f'[WARNING] Schema {self.path} without properties')
            self._children_initialized = True
            return self._children
        
        for propertyname, propertyvalue in properties.items():
            if 'properties' in propertyvalue or propertyvalue.get('type') == 'object':
                childschema = Schema(self.id + '/properties/' + propertyname, propertyname, self.spec)
                childschema._schemavalue = propertyvalue
                self._children.append(childschema)
            elif propertyvalue.get('type') == 'array' and 'items' in propertyvalue and 'properties' in propertyvalue['items']:
                childschema = Schema(self.id + '/properties/' + propertyname, propertyname, self.spec)
                childschema._schemavalue = propertyvalue['items']
                childschema._description = propertyvalue.get('description')
                childschema._isarray = True
                examples = propertyvalue.get('example')

                if examples:
                    for example in examples:
                        childschema._example = json.dumps(example)
                        break

                self._children.append(childschema)
            elif 'items' in propertyvalue and 'properties' not in propertyvalue['items']:
                childproperty = SchemaProperty(self.id + '/properties/' + propertyname, propertyname, self.spec)
                childproperty._property = propertyvalue['items']
                childproperty._isarray = True
                self._children.append(childproperty)
            else:
                childproperty = SchemaProperty(self.id + '/properties/' + propertyname, propertyname, self.spec)
                childproperty._property = propertyvalue
                self._children.append(childproperty)
        
        self._children_initialized = True
        return self._children

class SchemaProperty(Schema):
    def __init__(self, id, name, spec):
        super(SchemaProperty, self).__init__(id, name, spec)
        self._classname = self._packagename + '.property'
        self._property = None
        self._datatype = None

        if self.path and not self._property:
            key = self.path.replace('/', '.')
            self._property = OpenAPIModel.safe_get(key, self.spec)
    
    @property
    def val(self):
        return self._property
    
    @property
    def description(self):
        return self.val.get('description')
    
    @property
    def datatype(self):
        if not self._datatype:
            return self.val.get('type')
        else:
            return self._datatype

    @property
    def dataformat(self):
        return self.val.get('format')
    
    @property
    def example(self):
        return self.val.get('example')

    def build(self):
        prop = copy.deepcopy(self._objects_head)
        prop['class'] = self.classname
        prop['core.name'] = self.name
        prop['identity'] = self.id
        prop['core.description'] = self.description
        prop[self._attr_property_datatype] = self.datatype
        prop[self._attr_property_dataformat] = self.dataformat
        prop[self._attr_property_example] = self.example
        prop[self._attr_isarray] = self.isarray
        return prop

class PathItem(Identifier):
    def __init__(self, id, name, spec):
        super(PathItem, self).__init__(id, name, '', spec)
        self._classname = self._packagename + '.path'
        self._operations = []
        self._operations_initialized = False
    
    def build(self):
        pathitem = copy.deepcopy(self._objects_head)
        pathitem['class'] = self.classname
        #pathitem['core.name'] = self.name.replace('/', '', 1)
        pathitem['core.name'] = self.name
        pathitem['identity'] = self.id
        pathitem['core.description'] = ''
        return pathitem

    def operations(self):
        if self._operations_initialized:
            return self._operations
        
        val = self.spec.get('paths').get(self.name)
        
        for operationname, operationvalue in val.items():
            self._operations.append(
                Operation(self.id + '/' + operationname, operationname, operationvalue.get('description'), self.spec)
            )
        
        self._operations_initialized = True
        return self._operations

class Operation(Identifier):
    def __init__(self, id, name, description, spec):
        super(Operation, self).__init__(id, name, description, spec)
        self._classname = self._packagename + '.operation'
    
    def build(self):  
        operation = copy.deepcopy(self._objects_head)
        operation['class'] = self.classname
        operation['core.name'] = self.name
        operation['identity'] = self.id
        operation['core.description'] = self.description
        return operation


