FROM python

LABEL org.opencontainers.image.source="https://github.com/sitistas/bus_arrivals_application"

ADD test-requests.py .
ADD .env .
ADD overall_data_catalogue.csv .
ADD overall_data_sample.csv .

#Install dependencies
RUN pip install requests python-dotenv pandas geopy plotly dash

CMD [ "python", "test-requests.py", "-b 0.0.0.0:8050" ]

# docker pull konsitistas/bus_arrivals_application
# docker run -ti konsitistas/bus_arrivals_application
