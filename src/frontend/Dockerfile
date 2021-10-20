# build stage
FROM node:15-alpine as build
ADD ./vite.config.js /frontend/
ADD ./package*.json /frontend/
ADD ./yarn.lock /frontend/
ADD ./.npmrc  /frontend/
WORKDIR /frontend
RUN yarn
COPY . .
ARG NODE_ENV
ARG ENV
RUN yarn build

FROM nginx:1.21-alpine as deploy
RUN rm /etc/nginx/conf.d/default.conf && rm /etc/nginx/nginx.conf
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /frontend/dist /usr/share/nginx/html
RUN chown -R nginx:nginx /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]