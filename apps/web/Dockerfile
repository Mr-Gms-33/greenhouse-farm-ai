FROM node:20-alpine AS build
WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html

COPY --from=build /app/dist ./
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY nginx/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENV API_PROXY_URL=""

ENTRYPOINT ["/entrypoint.sh"]
