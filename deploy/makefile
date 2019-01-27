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

.PHONY: download-logs
download-logs:
	(cd project/manage; bash download-logs.sh)

.PHONY: download-plan
download-plan:
	(cd project/manage; bash download-plan.sh)

.PHONY: download-db
download-db:
	(cd project/manage; bash download-db.sh)

.PHONY: ssh
ssh:
	(cd project/manage; bash ssh.sh)
