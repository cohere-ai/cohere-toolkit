FROM nginx:alpine

RUN rm -f /etc/nginx/conf.d/*
ADD azure_compose_deploy/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD [ "nginx" , "-g" , "daemon off;" ]
