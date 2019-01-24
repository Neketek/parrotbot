.PHONY: all
all:

.PHONY: build-ami
build-ami:
	(cd ami; packer validate template.json && packer build template.json)

.PHONY: upload-project
upload-project:
	(cd project/upload; ./start.sh)

.PHONY: start-bot
start-bot:
	(cd project/manage; ./manage.sh start-bot.sh)

.PHONY: update-bot
update-bot:
	(cd project/manage; ./manage.sh update-bot.sh)

.PHONY: stop-bot
stop-bot:
	(cd project/manage; ./manage.sh stop-bot.sh)
