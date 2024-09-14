# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install required dependencies
RUN pip install --no-cache-dir Pillow iptcinfo3 langchain langchain_community

# Download the Python script from the GitHub repository
CMD ["python3"]