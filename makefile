.PHONY: all
all:

.PHONY: dcstop
dcstop:
	docker-compose down

.PHONY: dcbuild
dcbuild:
	docker-compose build --force-rm

.PHONY: dcdrun
dcdrun: dcstop dcbuild
	docker-compose run -d server

.PHONY: dcrun
dcrun: dcstop dcbuild
	docker-compose run server

.PHONY: dcrestart
dcrestart: dcstop dcrun

.PHONY: lsc
lsc:
	docker container ls
