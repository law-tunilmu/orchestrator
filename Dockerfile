# Use the official Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Expose the port on which the application will run
EXPOSE 8800

# Set environment variables
ARG PRODUCTION
ARG AUTH_BE
ARG TRANSACTION_BE
ARG COURSE_BE
ARG FORUM_BE

# set environment variables
ENV PRODUCTION=${PRODUCTION}
ENV AUTH_BE=${AUTH_BE}
ENV TRANSACTION_BE=${TRANSACTION_BE}
ENV COURSE_BE=${COURSE_BE}
ENV FORUM_BE=${FORUM_BE}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8800"]