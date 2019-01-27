source ../ssh-auth-vars.sh

FILE_LOCATION="/home/$SSH_USER/db.tar.gz"
FILE_NAME="db.tar.gz"
PREPARE_FILE_CMD="cd parrotbot/server/files/db && tar --exclude='readme.md' -zcvf $FILE_LOCATION ."

source ./download-file.sh
