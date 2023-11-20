# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app


# Copy the requirements.txt file into the container
COPY requirements.txt /app

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the SusDB source code into the container
COPY . /app

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app/src

# Define the entry command
ENTRYPOINT ["python", "/app/src/susdb_cli.py"]

