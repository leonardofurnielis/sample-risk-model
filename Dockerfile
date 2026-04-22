FROM registry.hub.docker.com/library/python:3.10.14-slim

# Create a directory for the application
WORKDIR /home/vcap/app

# Copy the requirements file initially to leverage Docker cache
COPY requirements.txt ./

# Install system dependencies and Python packages
RUN pip install --upgrade pip
RUN apt update \
    && pip install --no-cache-dir -r requirements.txt

COPY . . 

CMD ["python3", "main.py"]
# CMD ["gunicorn", "-b", "0.0.0.0:3000", "-c", "/home/vcap/app/main.py", "main:app"]
