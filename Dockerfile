FROM python

LABEL org.opencontainers.image.source="https://github.com/sitistas/bus_arrivals_application"

ADD bus.py .
ADD .env .
ADD overall_data_catalogue.csv .
ADD overall_data_sample.csv .

#Install dependencies
RUN pip install requests python-dotenv pandas geopy plotly dash

EXPOSE 8085

CMD [ "python", "bus.py"]
# ,"-b 0.0.0.0:8050", "app.app:server" ]

# docker pull konsitistas/bus_arrivals_application
# docker run -ti konsitistas/bus_arrivals_application
