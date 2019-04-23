# # Load the inventory
# from project.tools.parser import Parser
# from project import package_directory
#
# # TODO this should be replaced by accessing a Database in the future
# inventory_db = Parser.yaml(package_directory + "\\data\\inventory.yml")

from tinydb import TinyDB

db = TinyDB('db.json')
inventory_table = db.table('inventory')
submissions_table = db.table('submissions')