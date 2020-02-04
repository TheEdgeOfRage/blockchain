FROM python:3.8-alpine

WORKDIR /app
EXPOSE 80
ENV FLASK_APP=run:app \
	FLASK_ENV=production \
	PYTHONUNBUFFERED=1
CMD ["flask", "run", "-p", "80", "-h", "0.0.0.0"]

ADD requirements.txt run.py ./
RUN pip install -r requirements.txt

ADD blockchain/ ./blockchain/
