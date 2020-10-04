FROM nginx:1.19.0
ENV PYTHONBUFFERED 1

# enables live reload for windows
ENV CHOKIDAR_USEPOLLING 1

RUN apt-get update && \
    apt-get install -y python3.7 python3-pip && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

RUN apt-get update && \
    apt-get install -y build-essential openssl libssl-dev libpq-dev

ADD ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN pip install django-ckeditor

RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install -y nodejs

# popper.js wants a git depenency...
RUN apt-get update && \
    apt-get install -y git

RUN npm install -g parcel-bundler@1.12

COPY ./package.json /package.json
COPY ./package-lock.json /package-lock.json
RUN npm install

ADD /ui /ui
ADD /server /server

RUN cp /server/templates/base.html /base.html && \
    parcel build /base.html -d /build --public-url /static && \
    mkdir /compiled-templates && \
    mv build/base.html compiled-templates/base.html

ADD nginx.conf /etc/nginx/conf.d/default.conf

WORKDIR /server
RUN python manage.py collectstatic

CMD gunicorn -b 0.0.0.0:5000 app.wsgi:application --log-level debug --daemon \
    && sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf \
    && nginx -g 'daemon off;'
