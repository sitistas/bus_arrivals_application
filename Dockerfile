FROM python

ADD bus.py .
ADD .env .
ADD overall_data_catalogue.csv .
ADD overall_data_sample.csv .
ADD data.zip .

#Install dependencies
RUN pip install requests python-dotenv pandas geopy plotly dash

EXPOSE 8085

CMD [ "python", "bus.py"]

# docker pull konsitistas/bus_arrivals_application
# docker run -ti -p 8085:8085 konsitistas/bus_arrivals_application
