import requests
import xml.dom.minidom  # Beautify xml output
import zipfile
from dotenv import load_dotenv
import os
import json
import datetime

load_dotenv()

API_KEY = os.getenv('API_KEY')

# Δοκιμαστικό request
r = requests.get(
    'https://data.bus-data.dft.gov.uk/api/v1/dataset/464/?api_key={}'.format(API_KEY))
r2json = r.text
#JSON pretty print
r2json = json.loads(r2json)
r2json = json.dumps(r2json, indent=2)
print(r2json)

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
    # print(data)


xml_fname = archive.extract(x)

# or xml.dom.minidom.parseString(xml_string)
dom = xml.dom.minidom.parse(xml_fname)

#Name of current day
today=datetime.datetime.now()
today=today.strftime('%A')
print(today)

#Get Vehicle Journeys
vehiclejs=dom.getElementsByTagName('VehicleJourney')

#Δες ποια δρομολόγια εκτελούνται τη μέρα που θες (πχ Δευτέρα)
for elem in vehiclejs:
    days=elem.getElementsByTagName('DaysOfWeek')
    for day in days:
        x=day.getElementsByTagName('Monday')
        #Αν για ένα δρομολόγιο υπάρχει η Δευτέρα στις μέρες εκτέλεσης, τύπωσε την ώρα εκκίνησης
        if x!=[]:
            depttime=elem.getElementsByTagName('DepartureTime')
            print(depttime[0].firstChild.data)
# pretty_xml_as_string = dom.toprettyxml()
# print(pretty_xml_as_string)
