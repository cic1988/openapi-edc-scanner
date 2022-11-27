class OpenAPIModel():
    def __init__(self):
        """
        see model/model.xml
        """
        
        """ 1) class """
        self._packagename = 'com.informatica.ldm.openapi'
        self._class_endpoint = self._packagename + '.endpoint'
        self._class_info = self._packagename + '.info'
        self._class_externaldocs = self._packagename + '.externaldocs'
        self._class_schema = self._packagename + '.schema'
        self._class_property = self._packagename + '.property'

        """ 2) attribute """
        self._attr_endpoint_version = self._packagename + '.openapi'
        self._attr_infoversion = self._packagename + '.infoversion'
        self._attr_infotitle = self._packagename + '.infotitle'
        self._attr_infodescription = self._packagename + '.infodescription'
        self._attr_infotermsOfService = self._packagename + '.infotermsOfService'
        self._attr_infocontactemail = self._packagename + '.infocontactemail'
        self._attr_infolicensename = self._packagename + '.infolicensename'
        self._attr_externaldocs_url = self._packagename + '.externaldocsurl'
        self._attr_property_example = self._packagename + '.propertyexample'

        """ 2.1) attribute (inherited from base model) """
        self._attr_property_primarykey = 'com.infa.ldm.relational.PrimaryKeyColumn'
        self._attr_property_datatype = 'com.infa.ldm.relational.Datatype'
        self._attr_property_dataformat = 'com.infa.ldm.relational.FieldFormat'
        self._attr_property_nullable = 'com.infa.ldm.relational.Nullable'
        self._attr_property_maxlength = 'com.infa.ldm.relational.DatatypeLength'
        self._attr_property_scale = 'com.infa.ldm.relational.DatatypeScale'

        """ 3) association """
        self._association_resourceparanchild = 'core.ResourceParentChild'
        self._association_endpointinfo = self._packagename + '.endpointinfo'
        self._association_enndpointschema = self._packagename + '.endpointschema'
        self._association_schemaproperty = self._packagename + '.schemaproperty'

        """ 4) lineage (within the data source) """
        self._association_datasourcedataflow = 'core.DataSourceDataFlow'
        self._association_datasetdataflow = 'core.DataSetDataFlow'
        self._association_directionaldataflow = 'core.DirectionalDataFlow'
