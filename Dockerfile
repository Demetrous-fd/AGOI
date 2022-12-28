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

RUN apt-get update \
    && apt-get install -y \
        wget \
        libxrender1 \
        libfontconfig \
        libxtst6 \
        xz-utils \
        xfonts-base \
        xfonts-75dpi \
        libjpeg62-turbo \
        fontconfig

RUN set -ex && \
    wget -O wkhtmltopdf.deb https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb && \
    dpkg -i wkhtmltopdf.deb && \
    pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install && \
    rm -rf /root/.cache/


# Expose port 8000
EXPOSE 8000

RUN pipenv shell
# Use gunicorn on port 8000
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "AGOI.wsgi"]
