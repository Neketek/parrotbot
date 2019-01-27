source ../ssh-auth-vars.sh

FILE_LOCATION="/home/$SSH_USER/log.tar.gz"
FILE_NAME="log.tar.gz"
PREPARE_FILE_CMD="cd ~/parrotbot/server/files/log && tar --exclude='readme.md' -zcvf $FILE_LOCATION ."

source ./download-file.sh
