#!/bin/bash

if [ ! -d ../venv ]; then
	echo "Cloning virtual environment"
	git clone https://github.com/Choromanski/venv.git ../venv
fi

source ../venv/bin/activate

python manage.py db init
python manage.py db migrate
python manage.py db upgrade