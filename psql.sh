#!/bin/bash

if [ ! -d ../venv ]; then
	echo "Cloning virtual environment"
	git clone https://github.com/Choromanski/venv.git ../venv
fi

source ../venv/bin/activate

psql $DATABASE_URL