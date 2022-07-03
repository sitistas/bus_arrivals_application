import requests
import xml.dom.minidom  # Beautify xml output
import zipfile
from dotenv import load_dotenv
import os
import json
import datetime
import pandas

load_dotenv()

API_KEY = os.getenv('API_KEY')
# Το id παραμένει ίδιο στο πρώτο request και στο κατέβασμα του zip, οπότε μπορούμε να το περνάμε σαν όρισμα
id = input('Βάλε το Data ID: ')  # or 464
if id == '':
    id = '464'
# Όνομα γραμμής
line_name = input('Βάλε το όνομα της γραμμής: ')  # or 'SP'
if line_name == '':
    line_name = 'SP'

# Στο αρχείο overall_data_catalogue.csv υπάρχει αντιστοίχιση των γραμμών που περιλαμβάνονται σε κάθε id με το μοναδικό BODS_***** αρχείο, επομένως με την δημιουργία μιας βάσης δεδομένων (ή με ανάκληση από το csv), μπορούμε να επιλέγουμε την γραμμή που θέλουμε


def return_line_data(id, line_name):
    df = pandas.read_csv('overall_data_sample.csv')
    mask = (df['Line Name'] == line_name)  # & (df['Data ID'] == id)
    # ΔΕ ΛΕΙΤΟΥΡΓΕΙ ΣΩΣΤΑ, ΠΡΕΠΕΙ ΝΑ ΜΠΑΙΝΕΙ ΣΑΝ ΦΙΛΤΡΟ ΚΑΙ ΤΟ ID
    df_new = df[mask]
    print(df_new)
    file_name = df_new['TXC File Name'].iloc[0]
    print(df_new[['Operator', 'Line Name']])
    print(file_name)
    return file_name


# Δοκιμαστικό request
r = requests.get(
    'https://data.bus-data.dft.gov.uk/api/v1/dataset/{}/?api_key={}'.format(id, API_KEY))
r2json = r.text
# JSON pretty print
r2json = json.loads(r2json)
r2json = json.dumps(r2json, indent=2)
print(r2json)

# Δοκιμαστικό κατεβασμα zip file με xml αρχεία
url = 'https://data.bus-data.dft.gov.uk/timetable/dataset/{}/download/'.format(
    id)

r1 = requests.get(url)
open("data.zip", "wb").write(r1.content)


archive = zipfile.ZipFile('data.zip', 'r')
files = archive.namelist()

# print(files)

file_name = return_line_data(id, line_name)

with archive.open(file_name, "r") as fi:
    data = fi.read()
    # print(data)


xml_fname = archive.extract(file_name)

# or xml.dom.minidom.parseString(xml_string)
dom = xml.dom.minidom.parse(xml_fname)

# Name of current day
today = datetime.datetime.now()
today = today.strftime('%A')
print(today)

# Get Vehicle Journeys
vehiclejs = dom.getElementsByTagName('VehicleJourney')

# Δες ποια δρομολόγια εκτελούνται τη μέρα που θες (πχ Δευτέρα)
for elem in vehiclejs:
    days = elem.getElementsByTagName('DaysOfWeek')
    x = days[0].getElementsByTagName('Monday')
    # Αν για ένα δρομολόγιο υπάρχει η Δευτέρα στις μέρες εκτέλεσης, τύπωσε την ώρα εκκίνησης
    if x != []:
        depttime = elem.getElementsByTagName('DepartureTime')
        print(depttime[0].firstChild.data)
# pretty_xml_as_string = dom.toprettyxml()
# print(pretty_xml_as_string)
