import requests
from geopy.geocoders import Nominatim
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
id = int(input('Βάλε το Data ID: ') or 464)  # or 464
# Όνομα γραμμής
line_name = input('Βάλε το όνομα της γραμμής: ')  # or 'SP'
if line_name == '':
    line_name = 'SP'
# Όνομα μέρας
day = input('Διάλεξε μέρα: ')
if day not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Today']:
    day = 'Monday'
if day == 'Today':
    today = datetime.datetime.now()
    day = today.strftime('%A')
print(day)


# Στο αρχείο overall_data_catalogue.csv υπάρχει αντιστοίχιση των γραμμών που περιλαμβάνονται σε κάθε id με το μοναδικό BODS_***** αρχείο, επομένως με την δημιουργία μιας βάσης δεδομένων (ή με ανάκληση από το csv), μπορούμε να επιλέγουμε την γραμμή που θέλουμε


def return_line_data(id, line_name):
    df = pandas.read_csv('overall_data_catalogue.csv')
    df_new1 = df[df['Line Name'] == line_name]
    # print(df_new1)
    df_new = df_new1[df_new1['Data ID'] == id]
    # print(df_new)
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
lineOperator = r.json()['noc']
lineOperator = lineOperator[0]
print(lineOperator)

r1 = requests.get(url)
open("data.zip", "wb").write(r1.content)


archive = zipfile.ZipFile('data.zip', 'r')
files = archive.namelist()

# print(files)

file_name = return_line_data(id, line_name)  # TO BE FIXED
# file_name = 'BODS_PF0007157_12_20220129_0.xml'

with archive.open(file_name, "r") as fi:
    data = fi.read()
    # print(data)


xml_fname = archive.extract(file_name)

# or xml.dom.minidom.parseString(xml_string)
dom = xml.dom.minidom.parse(xml_fname)

# Get the departure's list for a particular line and day

# print(file_name)
def getDeps(day, line_name, dom):
    # Get all Vehicle Journeys
    depList = []
    journeyDict={}
    vehiclejs = dom.getElementsByTagName('VehicleJourney')
    # print(len(vehiclejs))
    # Δες ποια δρομολόγια εκτελούνται τη μέρα που θες (πχ Δευτέρα)
    for elem in vehiclejs:
        lineRef = elem.getElementsByTagName('LineRef')
        # Οι τελευταίοι χαρακτήρες (1 ή 2) του lineRef ενός VehicleJourney αντιστοιχούν στον αριθμό της γραμμής
        lineName = (lineRef[0].firstChild.data).rsplit(':', 1)
        # Αν η γραμμή του VehicleJourney αντιστοιχεί σε άλλη γραμμή από αυτή που θέλουμε
        if lineName[1] != line_name:
            continue

        days = elem.getElementsByTagName('DaysOfWeek')
        x = days[0].getElementsByTagName(day)
        # Αν για ένα δρομολόγιο υπάρχει η σχετική μέρα στις μέρες εκτέλεσης
        if x != []:
            deptTime = elem.getElementsByTagName('DepartureTime')[0].firstChild.data
            journeyPattern = elem.getElementsByTagName('JourneyPatternRef')[0].firstChild.data
            depList.append(deptTime)
            journeyDict[deptTime]=journeyPattern
    return [depList, journeyDict]

#Δημιουργία λεξικού που αντιστοιχείζει τους κωδικούς των στάσεων στα ονόματά τους
def getStops(dom):
    annotatedStops = dom.getElementsByTagName('AnnotatedStopPointRef')
    stops={}
    for stop in annotatedStops:
        stopRef=stop.getElementsByTagName('StopPointRef')[0].firstChild.data
        stopName=stop.getElementsByTagName('CommonName')[0].firstChild.data
        stops[stopRef]=stopName
    return stops


#JourneyPatternSectionsDictionary
def getJPSD(dom):
    JPSD={}
    JPSections=dom.getElementsByTagName('JourneyPatternSection')
    for section in JPSections:
        JPSStops = []
        stopPoints=section.getElementsByTagName('StopPointRef')
        JPSStops.append(stopPoints.item(0).firstChild.data)
        for i in range(1, len(stopPoints), 2):
            JPSStops.append(stopPoints.item(i).firstChild.data)
        JPSD[section.attributes['id'].value]=JPSStops
    return JPSD

#JourneyPatterns
def getJP(dom):
    JP={}
    
    JPatterns=dom.getElementsByTagName('JourneyPattern')
    for pattern in JPatterns:
        JPSList=[]
        JPSRefs = pattern.getElementsByTagName('JourneyPatternSectionRefs')
        for ref in JPSRefs:
            JPSList.append(ref.firstChild.data)
        JP[pattern.attributes['id'].value]=JPSList
    return JP

#Στάση ανα δρομολόγιο με βάση την ώρα του
def getStopsOfDept(stopsDict, JPSD, journeyPatterns, journeyPerDeparture, departure):
    stopsList = []
    jPattern=journeyPerDeparture[departure]
    JPSections = journeyPatterns[jPattern]
    for section in JPSections:
        for stop in JPSD[section]:
            stopsList.append(stopsDict[stop])
    return stopsList


#Λεξικό με τις στάσεις (κλειδί ο κωδικός τους)
stopsDict=getStops(dom)

#Λεξικό με τα JourneyPatternSections με κλειδί το ID τους
JPSD=getJPSD(dom)

journeyPatterns = getJP(dom)
# print(journeyPatterns)

#print(JPSD)

#Δρομολόγια και λεξικό με την αντιστοιχία ώρας αναχώρησης με journey pattern
[departureList, journeyPerDeparture] = getDeps(day, line_name, dom)

print("Οι στάσεις του πρώτου δρομολογίου της ημέρας:")
stopsList = getStopsOfDept(stopsDict, JPSD, journeyPatterns, journeyPerDeparture, departureList[0])
print(stopsList)

#livedata ID NEEDS TO BE FIXED
r2 = requests.get(
    'https://data.bus-data.dft.gov.uk/api/v1/datafeed/7865/?api_key={}'.format(API_KEY))
#Χρειάζεται 2ο αρχείο ή όχι;
open("livedata.xml", "wb").write(r2.content)

livedom = xml.dom.minidom.parse("livedata.xml")
livePositions = []
allBuses = livedom.getElementsByTagName('VehicleActivity')
for bus in allBuses:
    if bus.getElementsByTagName('OperatorRef')[0].firstChild.data==lineOperator:
        if bus.getElementsByTagName('LineRef')[0].firstChild.data.lower()==line_name:
            livePositions.append(bus.getElementsByTagName('Latitude')[0].firstChild.data+", "+bus.getElementsByTagName('Longitude')[0].firstChild.data)

print(livePositions)
geolocator=Nominatim(user_agent='bus')
for pos in livePositions:
    location = geolocator.reverse(pos)
    print(location.address)

# print(departureList)
# pretty_xml_as_string = dom.toprettyxml()
# print(pretty_xml_as_string)
