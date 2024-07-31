# Use an official Python runtime as a parent image
# FROM python:3.9-slim
FROM python:3.10

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

RUN apt-get install -y tesseract-ocr python3 python3-pip
RUN apt-get update && apt-get install -y default-jdk
RUN apt-get update && apt-get update && apt-get install -y cmake


ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

COPY eng.traineddata /usr/share/tesseract-ocr/5/tessdata/eng.traineddata

COPY mcr.traineddata /usr/share/tesseract-ocr/5/tessdata/mcr.traineddata



# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install opencv-python
RUN pip install tabula-py

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=server.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
