FROM python:3.11-bullseye
WORKDIR /app
RUN apt-get install fluidsynth
COPY . .
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0", "app:app"]