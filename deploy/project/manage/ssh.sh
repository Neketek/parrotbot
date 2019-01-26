source ../ssh-auth-vars.sh
set -x
ssh -i $ID_FILE $SSH_USER@$SSH_HOST
