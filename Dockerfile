FROM python:3.7

# Create a group and user to run our app
# ARG APP_USER=pheno
# RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=api.settings
WORKDIR /code

COPY requirements.txt /code/
COPY phenotype-reactor.ini /code/
COPY default_phenotype-reactor.ini /code/
COPY manage.py /code/
COPY api /code/api
COPY doc /code/doc

RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput


EXPOSE 9300
EXPOSE 9200

ENV UWSGI_WSGI_FILE=api/wsgi.py

# Base uWSGI configuration (you shouldn't need to change these):
ENV UWSGI_HTTP=:9300 UWSGI_MASTER=1 UWSGI_HTTP_AUTO_CHUNKED=1 UWSGI_HTTP_KEEPALIVE=1 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy

# Number of uWSGI workers and threads per worker (customize as needed):
ENV UWSGI_WORKERS=8 UWSGI_THREADS=4

# uWSGI static file serving configuration (customize or comment out if not needed):
# ENV UWSGI_STATIC_MAP="/static/=/code/static/" UWSGI_STATIC_EXPIRES_URI="/static/.*\.[a-f0-9]{12,}\.(css|js|png|jpg|jpeg|gif|ico|woff|ttf|otf|svg|scss|map|txt) 315360000"

# USER ${APP_USER}:${APP_USER}

# Start uWSGI
CMD ["uwsgi", "--show-config"]


