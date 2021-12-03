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
ARG NODE_ENV=production
ARG VITE_API_URL=https://app-sfm-api.azurewebsites.us/
ARG ENV=production
ARG VITE_API_AUTH_TOKEN=JZGq3%3ySCE&LjA5@deqQ@H4nt9f#d9x@o9iwE*Q2eKuXcUtDK&3pC5uMSUJWJRF
RUN yarn build
# CMD ["yarn", "serve"]

FROM nginx:alpine as deploy
COPY --from=build /frontend/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]