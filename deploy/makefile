.PHONY: all
all:

.PHONY: build-ami
build-ami:
	(cd ami; packer validate template.json && packer build template.json)

.PHONY: upload-project
upload-project:
	(cd project/upload; ./start.sh)
