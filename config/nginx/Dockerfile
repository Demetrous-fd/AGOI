FROM node:18.16.0-alpine3.18 as build-stage
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY . .
RUN cd frontend && npm run build

# production stage
FROM nginx:latest as production-stage
COPY --from=build-stage /app/frontend/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]