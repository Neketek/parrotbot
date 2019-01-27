source ../ssh-auth-vars.sh

FILE_LOCATION="/home/$SSH_USER/plan.json"
FILE_NAME="plan.json"
PREPARE_FILE_CMD="cd parrotbot/server/files/plan && python -m json.tool plan.json > $FILE_LOCATION"

source ./download-file.sh
