FROM node:21-alpine3.18
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
RUN npm prune --production
COPY . .
EXPOSE 8080
ENV ENV_RUN_AS "docker"
CMD [ "node" , "index.js"]