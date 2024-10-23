FROM nginx:alpine

RUN rm -f /etc/nginx/conf.d/*
ADD aws_copilot_deploy/nginx.conf /etc/nginx/nginx.conf

EXPOSE 8090

CMD [ "nginx" , "-g" , "daemon off;" ]
