.PHONY: all
all:

.PHONY: rmdb
rmdb:
	rm db.sqlite -f

.PHONY: srun
srun:
	python server.py

.PHONY: dsrun
dsrun:
	DEBUG=true python server.py

.PHONY: udignore
udignore:
	cat .gitignore > .dockerignore

.PHONY: pfreeze
pfreeze:
	pip freeze -l > requirements.txt
