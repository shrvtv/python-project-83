#!/usr/bin/env bash

curl -LsSf https://astral.sh/uv/install.sh | sh # Download uv
source $HOME/.local/bin/env
make install && psql -a -d $DATABASE_URL -f database.sql