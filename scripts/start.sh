#!/bin/sh

/app/scripts/pre_commands.sh

if [ "${IS_IN_PRODUCTION}" = '1' ]; then
  echo "Running Server"
  gunicorn core.wsgi:application --bind :"${DJANGO_PORT}";
else
  if [ "${PLAYGROUND_ON}" = '1' ]; then
    echo "Running Playground"
    jupyter notebook --ip=0.0.0.0 --port="${PLAYGROUND_PORT}" --allow-root &
  fi
  echo "Running Django Server"
  python manage.py runserver 0.0.0.0:"${DJANGO_PORT}";
fi