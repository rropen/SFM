# build stage
FROM node:16-slim as build
ARG NODE_AUTH_TOKEN
# ADD ./vite.config.js /src/
ADD ./package.json /frontend/
ADD ./yarn.lock /frontend/
ADD ./.npmrc.ci /frontend/.npmrc
WORKDIR /frontend
RUN yarn
COPY . .
ENV PATH ./node_modules/.bin:$PATH
ARG NODE_ENV
RUN yarn build
ARG ENV

FROM nginx:alpine as deploy
COPY --from=build /frontend/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]