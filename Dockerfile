FROM python

ADD bus.py .
ADD .env .
ADD overall_data_catalogue.csv .
ADD overall_data_sample.csv .
ADD data.zip .
ADD test_bus.py .
ADD functionsToBeTested.py .
ADD requirements.txt .

#Install dependencies
RUN pip install -r requirements.txt

EXPOSE 8085

CMD pytest test_bus.py >>results.txt ; cat results.txt; python bus.py

# docker pull konsitistas/bus_arrivals_application
# docker run -ti -p 8085:8085 konsitistas/bus_arrivals_application
