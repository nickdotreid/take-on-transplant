FROM nginx:1.19.0
ENV PYTHONBUFFERED 1

RUN apt-get update && \
    apt-get install -y python3.7 python3-pip && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

RUN apt-get update && \
    apt-get install -y build-essential openssl libssl-dev libpq-dev

ADD server/requirements.txt /server/requirements.txt
RUN pip install -r /server/requirements.txt

ADD /server /server

ADD /nginx.conf /nginx.conf

WORKDIR /server
RUN python manage.py collectstatic

CMD gunicorn -b 0.0.0.0:5000 app.wsgi:application --log-level debug --daemon \
    && cp /nginx.conf etc/nginx/conf.d/default.conf \
    && sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf \
    && nginx -g 'daemon off;'
