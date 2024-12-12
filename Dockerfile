FROM python:3.12.3-slim-bullseye
RUN pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    openssh-client \    
    openssl \
    procps \
    gnupg \
    wget \
    dos2unix \
    gcc \
    build-essential \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get -y install postgresql-client-16 \
    && rm -rf /var/lib/apt/lists/*


# Custom Package Directory
RUN mkdir /custom_packages
# Fetch Arguments from docker-compose.yml or CLI
ARG CI_JOB_TOKEN
ARG GITLAB_PRIVATE_ACCESS_TOKEN

# Split the concatenated URLs into an array and perform actions
ARG REGISTRY
RUN for URL in $(echo "$REGISTRY" | tr ',' ' '); do \
        FILE_NAME=$(basename "$URL"); \
        PACKAGE_PATH="/custom_packages/$FILE_NAME"; \
        if [ -n "$CI_JOB_TOKEN" ]; then \
            wget -O "$PACKAGE_PATH" --header "JOB-TOKEN: ${CI_JOB_TOKEN}" "$URL" && \
            pip install "$PACKAGE_PATH"; \
        elif [ -n "$GITLAB_PRIVATE_ACCESS_TOKEN" ]; then \
            wget -O "$PACKAGE_PATH" --header "PRIVATE-TOKEN: ${GITLAB_PRIVATE_ACCESS_TOKEN}" "$URL" && \
            pip install "$PACKAGE_PATH"; \
        else \
            echo "No valid token found for $URL"; \
        fi; \
    done

WORKDIR /app
COPY . .

# Set build argument
ARG SSH_KEY_PATH
ARG IS_IN_PRODUCTION

# Create the .ssh directory and conditionally copy the SSH key if not in production
RUN mkdir -p /root/.ssh && \
    if [ "$IS_IN_PRODUCTION" != "1" ] && [ -n "$SSH_KEY_PATH" ]; then \
    cp "$SSH_KEY_PATH" /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa; \
    fi
RUN pip install --force-reinstall -r requirements.txt
CMD ["/bin/sh", "-c", "dos2unix /app/scripts/* && chmod +x /app/scripts/* && /app/scripts/start.sh"]