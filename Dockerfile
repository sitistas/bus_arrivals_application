FROM python

ADD test-requests.py .
ADD .env .
ADD overall_data_catalogue.csv .
ADD overall_data_sample.csv .

#Install dependencies
RUN pip install requests python-dotenv pandas geopy

CMD [ "python", "test-requests.py" ]

# docker pull konsitistas/bus_arrivals_application
# docker run -ti konsitistas/bus_arrivals_application
