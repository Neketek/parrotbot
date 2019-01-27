DATE="$(date +'%Y-%m-%d %H:%M:%S')"
DEFAULT_DOWNLOAD_PATH="/home/$USER/Downloads/parrot.$DATE.$FILE_NAME"

echo -en "\nDEFAULT:$DEFAULT_DOWNLOAD_PATH\nPls, provide download path:"
read DOWNLOAD_PATH
DOWNLOAD_PATH=${DOWNLOAD_PATH:-"$DEFAULT_DOWNLOAD_PATH"}
echo -e "\n$DOWNLOAD_PATH"

if [ ! -z "$PREPARE_FILE_CMD" ]; then
   ssh -i $ID_FILE $SSH_USER@$SSH_HOST "$PREPARE_FILE_CMD"
fi
[ $? ] && scp -i $ID_FILE "$SSH_USER@$SSH_HOST:$FILE_LOCATION" "$DOWNLOAD_PATH"
[ $? ] && ssh -i $ID_FILE $SSH_USER@$SSH_HOST "rm -f $FILE_LOCATION"
