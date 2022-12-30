ARG node=node:16-alpine

# stage 1: install dependencies and build the app
FROM ${node} as frontend-build

LABEL maintainer="Pooria Soltani <pooria.ms@gmail.com>"

ARG INSTALL_PATH
WORKDIR ${INSTALL_PATH}

COPY package.json package-lock.json ./

RUN npm install --legacy-peer-deps

ARG REACT_APP_API_V1_STR
ARG REACT_APP_DEV_BACKEND_HOST
ARG REACT_APP_DEV_BACKEND_PORT
ARG REACT_APP_FRONTEND_ENV
ARG REACT_APP_FRONTEND_NAME
ARG REACT_APP_FRONTEND_URL
ARG REACT_APP_PROD_BACKEND_URL

COPY . .

ENV GENERATE_SOURCEMAP=false
RUN npm run build

# stage 2: copy the built app and run the nginx server
FROM nginx:1.15

ARG INSTALL_PATH
ARG NGINX_PATH=/usr/share/nginx/html

# Set working directory to nginx resources directory
WORKDIR ${NGINX_PATH}
# Remove default nginx static resources
RUN rm -rf ./*

# Copies static resources from builder stage
COPY --from=frontend-build ${INSTALL_PATH}/build .
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/conf.d
COPY robots.txt sitemap.txt ./

# Containers run nginx with global directives and daemon off
CMD ["nginx", "-g", "daemon off;"]
