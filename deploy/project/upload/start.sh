#!/usr/bin/env bash
clear

DEFAULT_BOT_ENV_FILE="$(realpath ../../../.env)"

echo 'Starting project uploding process. Pls, provide required vars...'
source ../ssh-auth-vars.sh

echo -ne "\nDEFAULT=$DEFAULT_DEPLOY_KEY_FILE\ngithub deploy key:"
read GITHUB_DEPLOY_KEY_FILE
GITHUB_DEPLOY_KEY_FILE=${GITHUB_DEPLOY_KEY:-"$DEFAULT_DEPLOY_KEY_FILE"}
echo -e "\n$GITHUB_DEPLOY_KEY"

echo -ne "\nDEFAULT=$DEFAULT_BOT_ENV_FILE\nbot .env file:"
read BOT_ENV_CONF_FILE
BOT_ENV_CONF_FILE=${BOT_ENV_CONF_FILE:-$DEFAULT_BOT_ENV_FILE}
echo -e "\n$BOT_ENV_CONF_FILE"

clear


echo 'Starting project upload process...'

scp -i $ID_FILE $GITHUB_DEPLOY_KEY_FILE $USER@$HOST:~/.ssh/id_rsa 1> /dev/null
if [ $? -eq 0 ]; then
  echo 'github deploy key copied successfully!'
else
  echo 'Stopped uploading!'
  kill $$
fi

ssh -i $ID_FILE $USER@$HOST 'bash' < ./scripts/pull-project.sh

scp -i $ID_FILE $BOT_ENV_CONF_FILE $USER@$HOST:~/parrotbot/.env 1> /dev/null
if [ $? -eq 0 ]; then
  echo 'Bot .env copied successfully!'
else
  echo "Bot .env file wasn't copied to the host! Bot will not launch!"
fi

echo 'Project upload finished successfully!'
