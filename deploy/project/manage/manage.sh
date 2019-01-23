source ../ssh-auth-vars.sh
ssh -i $ID_FILE $USER@$HOST 'bash' < "$1"
