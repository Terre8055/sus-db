# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the SusDB source code into the container
COPY . /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app

# Create a directory for logs and DBM files
RUN mkdir -p /tmp/data/sus-db
RUN touch /tmp/data/sus-db/susdb.log

# Install any dependencies
RUN pip install -r requirements.txt

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app/src

# Define the entry command
CMD ["python", "src/susdb_cli.py"]

CMD tail -f /dev/null

