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

RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install -y nodejs

# popper.js wants a git depenency...
RUN apt-get update && \
    apt-get install -y git

WORKDIR /take-on-transplant

RUN npm install -g parcel-bundler@1.12

ADD ./package.json ./package.json
ADD ./package-lock.json ./package-lock.json
ADD ./.sassrc ./.sassrc
RUN npm install

ADD ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN pip install django-ckeditor

ADD /ui /take-on-transplant/ui
ADD /server /take-on-transplant/server

RUN parcel build server/templates/base.html -d dist --public-url /static && \
    mkdir compiled-templates && \
    mv dist/base.html compiled-templates/base.html

ADD nginx.conf /etc/nginx/conf.d/default.conf

WORKDIR /take-on-transplant/server
RUN python manage.py collectstatic

CMD gunicorn -b 0.0.0.0:5000 app.wsgi:application --log-level debug --daemon \
    && sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf \
    && nginx -g 'daemon off;'
