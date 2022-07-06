import requests
from geopy.geocoders import Nominatim
import xml.dom.minidom  # Beautify xml output
import zipfile
from dotenv import load_dotenv
import os
import datetime
import pandas
import plotly.express as px
import dash
from dash import dcc
from dash import html, Input, Output

load_dotenv()

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

#Δημιουργία λίστας δρομολογίων και λεξικού αντιστοίχισης δρομολογίου-διαδρομής
def getDeps(day, line_name, dom):
    # Get all Vehicle Journeys
    depList = []
    journeyDict = {}
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
            deptTime = elem.getElementsByTagName('DepartureTime')[
                0].firstChild.data
            journeyPattern = elem.getElementsByTagName(
                'JourneyPatternRef')[0].firstChild.data
            depList.append(deptTime)
            journeyDict[deptTime] = journeyPattern
    return [depList, journeyDict]

# Δημιουργία λεξικού που αντιστοιχείζει τους κωδικούς των στάσεων στα ονόματά τους
def getStops(dom):
    annotatedStops = dom.getElementsByTagName('AnnotatedStopPointRef')
    stops = {}
    for stop in annotatedStops:
        stopRef = stop.getElementsByTagName('StopPointRef')[0].firstChild.data
        stopName = stop.getElementsByTagName('CommonName')[0].firstChild.data
        stops[stopRef] = stopName
    return stops


# Λεξικό που αντιστοιχίζει τα Journey Pattern Sections στη λίστα στάσεων που το καθένα περιλαμβάνει
def getJPSD(dom):
    JPSD = {}
    JPSections = dom.getElementsByTagName('JourneyPatternSection')
    for section in JPSections:
        JPSStops = []
        stopPoints = section.getElementsByTagName('StopPointRef')
        JPSStops.append(stopPoints.item(0).firstChild.data)
        for i in range(1, len(stopPoints), 2):
            JPSStops.append(stopPoints.item(i).firstChild.data)
        JPSD[section.attributes['id'].value] = JPSStops
    return JPSD

# Λεξικό που αντιστοιχίζει Journey Patterns στα Pattern Sections που αυτά περιλαμβάνουν
def getJP(dom):
    JP = {}

    JPatterns = dom.getElementsByTagName('JourneyPattern')
    for pattern in JPatterns:
        JPSList = []
        JPSRefs = pattern.getElementsByTagName('JourneyPatternSectionRefs')
        for ref in JPSRefs:
            JPSList.append(ref.firstChild.data)
        JP[pattern.attributes['id'].value] = JPSList
    return JP

# Λίστα στάσεων για ένα δρομολόγιο με βάση την ώρα του
def getStopsOfDept(stopsDict, JPSD, journeyPatterns, journeyPerDeparture, departure):
    stopsList = []
    jPattern = journeyPerDeparture[departure]
    JPSections = journeyPatterns[jPattern]
    for section in JPSections:
        for stop in JPSD[section]:
            stopsList.append(stopsDict[stop])
    return stopsList

# Σχεδίαση χάρτη με τις θέσεις των λεωφορείων live
def plotLiveData(latList, lonList, addresses):
    # Live Data Dataframe
    ldf = pandas.DataFrame({
        'Latitude': latList,
        'Longitude': lonList,
        'Address': addresses,
        'size': 1})
    fig = px.scatter_mapbox(ldf, lat="Latitude", lon="Longitude", hover_name="Address", size='size',
                            color_discrete_sequence=["blue"], zoom=12, height=800)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

# Λήψη συντεταγμένων των λεωφορείων από τα Live Data του BODS API
def getLiveData(lineOperator, line_name, livedom):
    latList = []
    lonList = []
    addresses = []
    allBuses = livedom.getElementsByTagName('VehicleActivity')
    for bus in allBuses:
        if bus.getElementsByTagName('OperatorRef')[0].firstChild.data == lineOperator:
            if bus.getElementsByTagName('LineRef')[0].firstChild.data.lower() == line_name.lower():
                latList.append(float(bus.getElementsByTagName(
                    'Latitude')[0].firstChild.data))
                lonList.append(float(bus.getElementsByTagName(
                    'Longitude')[0].firstChild.data))
    geolocator = Nominatim(user_agent='bus')
    for i in range(len(latList)):
        location = geolocator.reverse(str(latList[i])+", "+str(lonList[i]))
        addresses.append(location.address.split(",")[0])
    return [latList, lonList, addresses]

def downloadLiveData(liveid,API_KEY):
    # Request για λήψη των live data
    r2 = requests.get(
        'https://data.bus-data.dft.gov.uk/api/v1/datafeed/{}/?api_key={}'.format(liveid,API_KEY))
    # Αποθήκευση δεδομένων σε xml
    open("livedata.xml", "wb").write(r2.content)
    livedom = xml.dom.minidom.parse("livedata.xml")
    return livedom


API_KEY = os.getenv('API_KEY')
# Το id του dataset των timetables
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
# Το id του dataset των live data
liveid = int(input('Βάλε το Live Data ID: ') or 7865)  # or 7865

# Αρχικό request για τα timetables
r = requests.get(
    'https://data.bus-data.dft.gov.uk/api/v1/dataset/{}/?api_key={}'.format(id, API_KEY))

# Εξαγωγή δεδομένων από το αρχικό request
url = r.json()['url']
lineOperator = r.json()['noc']
lineOperator = lineOperator[0]

# r1 = requests.get(url)
# open("data.zip", "wb").write(r1.content)

# Ανάγνωση του αρχείου zip που έχει τα timetables και επιλογή του κατάλληλου xml αρχείου για τη γραμμή που επιλέξαμε
archive = zipfile.ZipFile('data.zip', 'r')
files = archive.namelist()
file_name = return_line_data(id, line_name)
with archive.open(file_name, "r") as fi:
    data = fi.read()

xml_fname = archive.extract(file_name)

dom = xml.dom.minidom.parse(xml_fname)

# Λεξικό με τις στάσεις (κλειδί ο κωδικός τους)
stopsDict = getStops(dom)

# Λεξικό με τις στάσεις ανά Journey Pattern Sections
JPSD = getJPSD(dom)

# Λεξικό με τα Journey Pattern Sections ανά Journey Pattern
journeyPatterns = getJP(dom)

# Λίστα με δρομολόγια και λεξικό με το journey pattern ανά δρομολόγιο (κλειδί η ώρα)
[departureList, journeyPerDeparture] = getDeps(day, line_name, dom)

print('Ώρες αναχώρησης')
for dep in departureList:
    print(dep)
deptTime = input('Διάλεξε ώρα αναχώρησης για να δεις τις στάσεις: ')
if deptTime not in departureList:
    print("Οι στάσεις του πρώτου δρομολογίου της ημέρας:")
    stopsList = getStopsOfDept(
        stopsDict, JPSD, journeyPatterns, journeyPerDeparture, departureList[0])
    print(stopsList)
# Αν εισαχθεί μη έγκυρη ώρα
else:
    print("Στάσεις:")
    stopsList = getStopsOfDept(
        stopsDict, JPSD, journeyPatterns, journeyPerDeparture, deptTime)
    print(stopsList)

#Λήψη live δεδομένων
livedom = downloadLiveData(liveid,API_KEY)

# Αποθήκευση συντεταγμένων live δεδομένων και δημιουργία server αν τα δεδομένα δεν είναι κενά
[latList, lonList, addresses] = getLiveData(lineOperator, line_name, livedom)
if len(latList)>0:
    fig = plotLiveData(latList, lonList, addresses)
    # fig.show()


    app = dash.Dash()
    app.layout = html.Div([
        dcc.Graph(figure=fig, id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=10*1000,  # in milliseconds
            n_intervals=0)
    ])


    @app.callback(Output('live-update-graph', 'figure'),
                Input('interval-component', 'n_intervals'))
    def update_graph_live(interval):
        # latList[0] += 0.0002 #Fake motion if needed for showcase
        livedom = downloadLiveData(liveid,API_KEY)
        [latList, lonList, addresses] = getLiveData(lineOperator, line_name, livedom)
        if len(latList)>0:
            fig = plotLiveData(latList, lonList, addresses)
        return fig

    app.run(
        host='0.0.0.0',
        port='8085')
else:
    print('No Live Data!')