from prance import ResolvingParser
from parser.openapi import OpenAPIParser

parser = ResolvingParser('./example/petstore3.json')
parser = OpenAPIParser(parser.specification, './test2')
parser.convert_objects(True)
parser.convert_links(True)
parser.zip_metadata()
