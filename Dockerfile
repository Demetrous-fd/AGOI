# Set Python environment variable
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set work directory called `app`
RUN mkdir -p /app
WORKDIR /app

# Copy local project
COPY . /app/

RUN set -ex && \
    apt-get install wkhtmltopdf \
    pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install && \
    rm -rf /root/.cache/


# Expose port 8000
EXPOSE 8000

RUN pipenv shell
# Use gunicorn on port 8000
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "AGOI.wsgi"]