import requests
import xml.dom.minidom  # Beautify xml output
import zipfile
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')

# Δοκιμαστικό request
r = requests.get(
    'https://data.bus-data.dft.gov.uk/api/v1/dataset/464/?api_key={}'.format(API_KEY))
print(r.json())

# Δοκιμαστικό κατεβασμα zip file με xml αρχεία
url = 'https://data.bus-data.dft.gov.uk/timetable/dataset/464/download/'

r1 = requests.get(url)
open("data.zip", "wb").write(r1.content)


archive = zipfile.ZipFile('data.zip', 'r')
files = archive.namelist()

# print(files)

x = files[0]
with archive.open(x, "r") as fi:
    data = fi.read()
    print(data)


xml_fname = archive.extract(x)

# or xml.dom.minidom.parseString(xml_string)
dom = xml.dom.minidom.parse(xml_fname)
pretty_xml_as_string = dom.toprettyxml()
print(pretty_xml_as_string)
