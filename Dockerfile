# Use the official Python 3.10.13 image from the Docker Hub
FROM python:3.10.13-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download only the NLTK stopwords
RUN python -m nltk.downloader stopwords

# Copy the rest of the application code into the container
COPY . /app

# Expose the port that the app will run on
EXPOSE 8000

# Command to run the application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
