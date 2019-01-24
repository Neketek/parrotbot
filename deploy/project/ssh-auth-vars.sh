clear

DEFAULT_KEY_DIR="/home/$USER/.ssh/parrotbot"
DEFAULT_USER=ubuntu

echo -ne "DEFAULT:$DEFAULT_KEY_DIR\nKeys folder:"
read KEY_FOLDER
KEY_DIR=${KEY_DIR:-"$DEFAULT_KEY_DIR"}
echo -e "\n$KEY_DIR"

DEFAULT_HOST_FILE="$KEY_DIR/host"
if [ -f "$DEFAULT_HOST_FILE" ]; then
  DEFAULT_HOST=$(cat $DEFAULT_HOST_FILE || echo 'None')
  echo -en "\nDEFAULT:$DEFAULT_HOST from $DEFAULT_HOST_FILE"
else
  echo -en "\nDEFAULT:$DEFAULT_HOST_FILE does not exist. Can't pull default host."
fi

echo -ne "\nec2 ssh hostname or ip:"
read SSH_HOST
SSH_HOST=${SSH_HOST:-$DEFAULT_HOST}
echo -e "\n$SSH_HOST"

echo -ne "\nDEFAULT=$DEFAULT_USER\nec2 ssh user:"
read SSH_USER
SSH_USER=${SSH_USER:-"$DEFAULT_USER"}
echo -e "\n$SSH_USER"

DEFAULT_ID_FILE="$KEY_DIR/key"
echo -ne "\nDEFAULT=$DEFAULT_ID_FILE\nec2 ssh key file":
read ID_FILE
ID_FILE=${ID_FILE:-"$DEFAULT_ID_FILE"}
echo -e "\n$ID_FILE"
