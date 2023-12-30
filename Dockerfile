FROM python:3.10-slim

WORKDIR /app

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    software-properties-common \
    unzip \
    firefox-esr

# Geckodriver 설치
RUN GECKODRIVER_VERSION=$(wget --no-verbose -O - "https://api.github.com/repos/mozilla/geckodriver/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/') \
    && wget -q -O - "https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz" | tar -xz -C /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN ["chmod", "+x", "./entrypoint.sh"]

CMD ["./entrypoint.sh"]