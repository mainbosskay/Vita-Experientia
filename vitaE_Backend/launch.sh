#!/usr/bin/env zsh
# Script configures environment and launches backed server

# Load configuration settings from .env.local file
export $(grep -v '^#' .env.local | xargs)

# Start backend server
python3 -m api.v1.server

# For bash script
# (!/usr/bin/env bash)
# Script configures environment and launches backend server

# declare -A ENV_VARS
# file_lines=()

# Read environment variables from the .env.local file
# readarray -t file_lines < <(cat .env.local)
# for ((indx = 0; indx < "${#file_lines[@]}"; indx++)) do 
#	line="${file_lines[indx]}"
#	ENV_VARS["$(echo "$line" | cut -d ':' -f1)"]="$(echo "$line" | cut -d ' ' -f2-)"
# done

# Set environment variables and start the backend server
# env DATABASE_URL="${ENV_VARS['DATABASE_URL']}" \
#	HOST="${ENV_VARS['HOST']}" \
#	IMG_PUB_KEY="${ENV_VARS['IMG_PUB_KEY']}" \
#   IMG_PRIV_KEY="${ENV_VARS['IMG_PRIV_KEY']}" \
#	IMG_URL_ENDPNT="${ENV_VARS['IMG_URL_ENDPNT']}" \
#	GMAIL_SENDER="${ENV_VARS['GMAIL_SENDER']}" \
#   FRONTEND_DOMAIN="${ENV_VARS['FRONTEND_DOMAIN']}" \
#	APP_SECRET_KEY="${ENV_VARS['APP_SECRET_KEY']}" \
#	python3 -m api.v1.server
