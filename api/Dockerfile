FROM python:3.8-bullseye
WORKDIR /app
RUN apt-get update
RUN apt-get install fluidsynth -y
COPY requirements.txt .
COPY app.py .
COPY config.py .
COPY figaro.py .
COPY figaro-expert.ckpt /
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0", "app:app"]