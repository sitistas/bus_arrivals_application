# Το αρχείο αυτό περιλαμβάνει 2 συναρτήσεις των οποίων ελέγχεται η ορθότητα,
# ώστε να μη χρειάζεται να τρέχουμε όλοκληρη την εφαρμογή bus.py και τον server όταν
# θέλουμε απλά να ελέγξουμε την ορθότητα κάποιων μόνο συναρτήσεων

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

def getStops(dom):
    annotatedStops = dom.getElementsByTagName('AnnotatedStopPointRef')
    stops = {}
    for stop in annotatedStops:
        stopRef = stop.getElementsByTagName('StopPointRef')[0].firstChild.data
        stopName = stop.getElementsByTagName('CommonName')[0].firstChild.data
        stops[stopRef] = stopName
    return stops