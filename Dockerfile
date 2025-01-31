# Create a base image
FROM python:slim
LABEL org.opencontainers.image.source="https://github.com/six-two/self-unzip.html"
RUN pip install --no-cache-dir --root-user-action=ignore pycryptodomex

# Install the app
COPY . /app
RUN pip install --root-user-action=ignore /app

# Just for convenience / app configuration
WORKDIR /share
VOLUME /share
ENTRYPOINT ["/usr/local/bin/self-unzip-html"]
CMD ["--help"]
