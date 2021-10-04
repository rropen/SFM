# build stage
FROM node:15.14.0-alpine3.12 as build
ADD ./package*.json /frontend/
WORKDIR /frontend

# Auth Token for Vue Cobalt
ARG NODE_AUTH_TOKEN
COPY .npmrc.ci .npmrc 

RUN yarn
COPY . .
ENV PATH ./node_modules/.bin:$PATH
CMD ["yarn", "serve"]
ARG NODE_ENV
ARG ENV

EXPOSE 3000
