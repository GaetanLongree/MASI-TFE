# # Load the inventory
# from project.tools.parser import Parser
# from project import package_directory
#
# # TODO this should be replaced by accessing a Database in the future
# inventory_db = Parser.yaml(package_directory + "\\data\\inventory.yml")
import os
from tinydb import TinyDB
from project import package_directory


db = TinyDB(os.path.join(package_directory, 'db.json'))
inventory_table = db.table('inventory')
submissions_table = db.table('submissions')