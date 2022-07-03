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
# Όνομα μέρας
day = input('Διάλεξε μέρα: ')
if day not in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','Today']:
    day='Monday'
if day=='Today':
    today = datetime.datetime.now()
    day = today.strftime('%A')
print(day)


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

# JSON pretty print
# r2json = r.text
# r2json = json.loads(r2json)
# r2json = json.dumps(r2json, indent=2)
# print(r2json)

# Δοκιμαστικό κατεβασμα zip file με xml αρχεία
url = r.json()['url']

r1 = requests.get(url)
open("data.zip", "wb").write(r1.content)


archive = zipfile.ZipFile('data.zip', 'r')
files = archive.namelist()

# print(files)

# file_name = return_line_data(id, line_name) TO BE FIXED
file_name = 'BODS_PF0007157_12_20220129_0.xml'

with archive.open(file_name, "r") as fi:
    data = fi.read()
    # print(data)


xml_fname = archive.extract(file_name)

# or xml.dom.minidom.parseString(xml_string)
dom = xml.dom.minidom.parse(xml_fname)

#Get the departure's list for a particular line and day
def getDeps(day, line_name):
# Get all Vehicle Journeys
    depList=[]
    vehiclejs = dom.getElementsByTagName('VehicleJourney')

    # Δες ποια δρομολόγια εκτελούνται τη μέρα που θες (πχ Δευτέρα)
    for elem in vehiclejs:
        lineRef=elem.getElementsByTagName('LineRef')
        #Οι τελευταίοι χαρακτήρες (1 ή 2) του lineRef ενός VehicleJourney αντιστοιχούν στον αριθμό της γραμμής
        lineName=(lineRef[0].firstChild.data).rsplit(':',1)
        #Αν η γραμμή του VehicleJourney αντιστοιχεί σε άλλη γραμμή από αυτή που θέλουμε
        if lineName[1]!=line_name:
            continue
    
        days = elem.getElementsByTagName('DaysOfWeek')
        x = days[0].getElementsByTagName(day)
        # Αν για ένα δρομολόγιο υπάρχει η σχετικέ μέρα στις μέρες εκτέλεσης, τύπωσε την ώρα εκκίνησης
        if x != []:
            depttime = elem.getElementsByTagName('DepartureTime')
            depList.append(depttime[0].firstChild.data)
    return depList

departureList=getDeps(day, line_name)
print(departureList)
# pretty_xml_as_string = dom.toprettyxml()
# print(pretty_xml_as_string)
