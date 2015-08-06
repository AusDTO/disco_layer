FROM ubuntu:14.04
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python-dev
RUN apt-get install -y gcc binutils
RUN apt-get install -y ssh-client
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y libxml2-dev libxslt1-dev libxml2 libxslt1-dev zlib1g-dev
RUN apt-get install -y python python-pip
RUN apt-get install -y libpq-dev git
ENV SRC=./
ENV HOME=/opt
ENV PROJ=/opt/disco_service
RUN groupadd -r disco && useradd -r -g disco disco
WORKDIR $HOME
RUN mkdir media static logs
#VOLUME ["$HOME/media/", "$HOME/logs/"]
COPY $SRC $PROJ
RUN chown -R disco:disco $HOME
WORKDIR $PROJ
RUN pip install -r requirements.txt
RUN python manage.py migrate
#COPY ./run.sh /
EXPOSE 80
USER disco
#ENTRYPOINT ["/run.sh"]
ENTRYPOINT ["./run.sh"]
