DEFAULT_KEY_FOLDER="/home/$USER/.ssh/parrotbot"
DEFAULT_DEPLOY_KEY_FILE="$DEFAULT_KEY_FOLDER/deploy"
DEFAULT_ID_FILE="$DEFAULT_KEY_FOLDER/key"
DEFAULT_USER=ubuntu

echo -ne "\nec2 ssh hostname or ip:"
read SSH_HOST
echo -e "\n$SSH_HOST"

echo -ne "\nDEFAULT=$DEFAULT_USER\nec2 ssh user:"
read SSH_USER
SSH_USER=${SSH_USER:-"$DEFAULT_USER"}
echo -e "\n$SSH_USER"

echo -ne "\nDEFAULT=$DEFAULT_ID_FILE\nec2 ssh key file":
read ID_FILE
ID_FILE=${ID_FILE:-"$DEFAULT_ID_FILE"}
echo -e "\n$ID_FILE"
