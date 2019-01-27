source ../ssh-auth-vars.sh
DATE="$(date +'%Y-%m-%d %H:%M:%S')"
DEFAULT_DOWNLOAD_PATH="/home/$USER/Downloads/parrot.$DATE.log.tar.gz"

AR_FILE_LOCATION="/home/$SSH_USER/log.tar.gz"
CMD="cd ~/parrotbot/server/files/log && tar --exclude='readme.md' -zcvf $AR_FILE_LOCATION ."

echo -en "\nDEFAULT:$DEFAULT_DOWNLOAD_PATH\nPls, provide download path:"
read DOWNLOAD_PATH
DOWNLOAD_PATH=${DOWNLOAD_PATH:-"$DEFAULT_DOWNLOAD_PATH"}
echo -e "\n$DOWNLOAD_PATH"

ssh -i $ID_FILE $SSH_USER@$SSH_HOST "$CMD"
scp -i $ID_FILE "$SSH_USER@$SSH_HOST:$AR_FILE_LOCATION" "$DOWNLOAD_PATH"
ssh -i $ID_FILE $SSH_USER@$SSH_HOST "rm -f $AR_FILE_LOCATION"
