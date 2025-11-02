#!/bin/sh



if [ "$RUN_MIGRATIONS" = "true" ]; then
  # Create migrations for the service app
  python bloggin_system/manage.py makemigrations service

  # Apply database migrations
  python bloggin_system/manage.py migrate
fi

# Execute the command passed to the script
exec "$@"