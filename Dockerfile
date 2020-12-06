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

ADD ./fixtures /take-on-transplant/fixtures
ADD ./icons /take-on-transplant/icons
ADD ./ui /take-on-transplant/ui
ADD ./server /take-on-transplant/server
ADD ./templates /take-on-transplant/templates

ADD nginx.conf /etc/nginx/conf.d/default.conf

WORKDIR /take-on-transplant/server
RUN npm run templates-build
RUN python manage.py collectstatic

CMD sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf \
    && honcho start prod nginx
