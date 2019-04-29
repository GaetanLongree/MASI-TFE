import os
import platform

package_directory = os.path.dirname(os.path.abspath(__file__))
current_directory = os.getcwd()
os_family = platform.system()
print(package_directory)