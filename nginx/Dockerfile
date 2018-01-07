#Not working, needs to be a proxy.

FROM nginx:latest

RUN apt-get update
RUN apt-get install --no-install-recommends --no-install-suggests software-properties-common
RUN add-apt-repository ppa:certbot/certbot
RUN apt-get update
RUN apt-get install --no-install-recommends --no-install-suggests python-certbot-nginx
RUN certbot --nginx

ADD docker-entrypoint-initdb.d/* /docker-entrypoint-initdb.d/
