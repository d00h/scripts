FROM python:3.12 

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt
COPY workout workout

ARG OPENAI_API_KEY

entrypoint ["python"]
