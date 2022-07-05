from dotenv import load_dotenv
import functionsToBeTested
import xml.dom.minidom
import os
import requests
import pandas
import zipfile

def return_line_data(id, line_name):
    df = pandas.read_csv('overall_data_catalogue.csv')
    df_new1 = df[df['Line Name'] == line_name]
    df_new = df_new1[df_new1['Data ID'] == id]
    file_name = df_new['TXC File Name'].iloc[0]
    print(df_new[['Operator', 'Line Name']])
    print(file_name)
    return file_name

load_dotenv()
id= 464
API_KEY = os.getenv('API_KEY')
r = requests.get('https://data.bus-data.dft.gov.uk/api/v1/dataset/{}/?api_key={}'.format(id, API_KEY))
url = r.json()['url']
# r1 = requests.get(url)
# open("data.zip", "wb").write(r1.content)
archive = zipfile.ZipFile('data.zip', 'r')

# Λήψη δεδομένων για τη γραμμή 5 του (προεπιλεγμένου) dataset 464 με τον ίδιο τρόπο που λαμβάνουμε τα δεδομένα στο bus.py
id= 464
API_KEY = os.getenv('API_KEY')
r = requests.get('https://data.bus-data.dft.gov.uk/api/v1/dataset/{}/?api_key={}'.format(id, API_KEY))
url = r.json()['url']
# r1 = requests.get(url)
# open("data.zip", "wb").write(r1.content)
archive = zipfile.ZipFile('data.zip', 'r')
file_name = return_line_data(id, '5')
with archive.open(file_name, "r") as fi:
    data = fi.read()
xml_fname = archive.extract(file_name)
dom = xml.dom.minidom.parse(xml_fname)

# Ώρες δρομολογίων και αντιστοίχιση αυτών με τις διαδρομές που ακολουθούν (Journey Patterns) για τη μέρα Δευτέρα
expected_answer_1=[['07:26:00', '07:45:00', '07:56:00', '08:26:00', '08:56:00', '09:56:00', '10:56:00', '11:56:00', '12:56:00', '13:56:00', '15:15:00', '14:56:00', '15:26:00', '15:56:00', '16:26:00', '16:56:00', '17:56:00'], {'07:26:00': 'JP1', '07:45:00': 'JP2', '07:56:00': 'JP3', '08:26:00': 'JP4', '08:56:00': 'JP3', '09:56:00': 'JP3', '10:56:00': 'JP3', '11:56:00': 'JP3', '12:56:00': 'JP3', '13:56:00': 'JP3', '15:15:00': 'JP5', '14:56:00': 'JP3', '15:26:00': 'JP3', '15:56:00': 'JP3', '16:26:00': 'JP6', '16:56:00': 'JP3', '17:56:00': 'JP6'}]
# Λεξικό των στάσεων (key: το id τους, value: το όνομα τους) της γραμμής 5
expected_answer_2={'260007373': 'Albany Street', '260007361': 'Albany Street', '260007234': 'Ashby Square', '260007275': 'Beacon Drive', '260007203': 'Belton Road', '260007208': 'Belton Road', '260007476': 'Blackbrook Road', '260007327': 'Booth Wood Primary School', '260007370': 'Burns Road', '260007364': 'Burns Road', '260007453': 'Butterley Drive', '260007384': 'Charnwood College', '260007385': 'Charnwood College', '260007270': 'Cleveland Road', '260007359': 'Cross Hill Lane', '260007372': 'Deane Street', '260007362': 'Deane Street', '260007205': 'Derby Road', '260007206': 'Derby Road', '260007363': 'Epinal Way', '260007371': 'Epinal Way', '260007271': 'Farndale Drive', '260007272': 'Farnham Road', '260007479': 'Fennel Street', '260007368': 'Garendon Road', '260007439': 'Grasmere Road', '260007444': 'Grassholme Drive', '260070060': 'Green', '260007469': 'Hermitage Road', '260080201': 'Herrick Road', '260006542': 'High Street', '260007426': 'Jitty', '260018577': 'Laurel Road', '260070067': 'Ledbury Road', '260007310': 'Lemontree Lane', '260007207': 'Leopold Street', '260007204': 'Leopold Street', '260070063': 'Lingdale Close', '260007438': 'Manor Road', '260070064': 'Maple Road South', '260007422': 'New Street', '260007308': 'Outwoods Edge School', '260070066': 'Poplar Road', '260007452': 'Redmires Close', '260070062': 'Rivington Drive', '260007291': 'Royland Road', '260007367': 'Rupert Brooke Road', '260007366': 'Rupert Brooke Road', '260007273': 'Sharpley Road', '260007349': 'Shops', '260007309': 'Spindle Road', '260007437': 'Swan Street', '260007369': 'Tennyson Road', '260007365': 'Tennyson Road', '260007338': 'Tesco', '260070215': 'The Rushes', '260007374': 'Tyler Avenue', '260007360': 'Tyler Avenue', '260007306': 'Walnut Road', '260070065': 'Walnut Road', '260007335': 'Wards End', '260007324': 'Windleden Road'}

def test_depTimes():
    output = functionsToBeTested.getDeps('Monday','5',dom)
    assert output==expected_answer_1

def test_stops():
    output = functionsToBeTested.getStops(dom)
    assert output==expected_answer_2