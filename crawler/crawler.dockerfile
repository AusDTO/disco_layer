# This is the crawler compose file, will need to be integrated later
FROM node:latest
COPY . /src
RUN cd /src; npm install
RUN cd /src; node testRegex.js
