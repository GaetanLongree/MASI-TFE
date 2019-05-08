FROM python:3

WORKDIR /usr/src/app

COPY api_srv/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD api_srv/ ./api_srv/

EXPOSE 7676

CMD [ "python", "-m", "api_srv" ]