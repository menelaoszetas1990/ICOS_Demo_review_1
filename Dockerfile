# Use the official Python 3.11 image as the base image
FROM python:3.11
USER root

# Set the working directory in the container
WORKDIR /usr/src/

# Copy the dependencies file to the container
COPY requirements.txt .

# Copy the content of the local src directory to the working directory
COPY src/ .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -m pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow_cpu-2.14.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

# Specify the command to run on container start
CMD [ "python", "main.py" ]
