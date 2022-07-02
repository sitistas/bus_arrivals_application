FROM python

ADD test-requests.py .

#Install dependencies
RUN pip install requests python-dotenv

CMD [ "python", "test-requests.py" ]

# docker build -t python-test .
# docker run python-test