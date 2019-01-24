cd ~
KNOWN_HOSTS=.ssh/known_hosts
PROJECT_DIR=parrotbot
if [ ! -f $KNOWN_HOSTS ] || ! grep -q github.com $KNOWN_HOSTS; then
  chmod 600 .ssh/id_rsa
  ssh-keyscan github.com >> $KNOWN_HOSTS
else
  echo "$KNOWN_HOSTS already has github.com entry"
fi

mkdir $PROJECT_DIR 2> /dev/null
cd $PROJECT_DIR
make dcstop
git init 2> /dev/null
git remote add origin git@github.com:Neketek/parrotbot.git 2> /dev/null
git pull origin master
echo 'Project pulled successfully!'
