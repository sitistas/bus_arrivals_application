# bus_arrivals_application
Πρότζεκτ στα πλαίσια του μαθήματος "Προηγμένες Τεχνικές Προγραμματισμού"

- Χρήση δεδομένων από [το Bus Open Data Service (BODS)](https://data.bus-data.dft.gov.uk/), που παρέχει ώρες δρομολογίων, θέσεις λεωφορείων και άλλες πληροφορίες για την Αγγλία
- Κλήση δεδομένων μέσω API, αποτελέσματα σε JSON & XML αρχεία, από τα οποία λαμβάνεται η πληροφορία
- Τα δεδομένα των timetables έχουν την μορφή που περιγράφεται στο [TransXChange format](https://pti.org.uk/system/files/files/TransXChange_UK_PTI_Profile_v1.1.A.pdf), οπότε μπορούμε να ανακτήσουμε τα δεδομένα για 1 ή παραπάνω operators