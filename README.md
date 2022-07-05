# bus_arrivals_application
Πρότζεκτ στα πλαίσια του μαθήματος "Προηγμένες Τεχνικές Προγραμματισμού"

Δημιουργοί:
- Σιτήστας Κωνσταντίνος Κυριάκος, 1066577
- Χαλαντζούκας Φοίβος, 1066579

- Χρήση δεδομένων από [το Bus Open Data Service (BODS)](https://data.bus-data.dft.gov.uk/), που παρέχει ώρες δρομολογίων, θέσεις λεωφορείων και άλλες πληροφορίες για την Αγγλία
- Κλήση δεδομένων μέσω API, αποτελέσματα σε JSON & XML αρχεία, από τα οποία λαμβάνεται η πληροφορία
- Τα δεδομένα των timetables έχουν την μορφή που περιγράφεται στο [TransXChange format](https://pti.org.uk/system/files/files/TransXChange_UK_PTI_Profile_v1.1.A.pdf), οπότε μπορούμε να ανακτήσουμε τα δεδομένα για 1 ή παραπάνω operators

- Διαδικασία δημιουργίας GitHub Workflow για build Docker Image:
    - Δημιουργία secrets στο GitHub Repo για εισαγωγή του Docker Account Username και ενός Personal Access Toekn
    - GitHub Actions --> Configuration του Docker Image workflow
    - Configure docker-image.yml file, και δημιουργία του .env αρχείου μέσω του αρχείου αυτού
    - Το GitHub Action αυτόματα μας δείχνει αν είναι επιτυχημένη η εκτέλεση του workflow ή όχι, και αν δεν είναι, κάτι εμποδίζει την δημιουργία του image.

## How to run:
- docker pull konsitistas/bus_arrivals_application
- docker run -ti -p 8085:8085 konsitistas/bus_arrivals_application
