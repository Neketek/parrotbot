.PHONY: all
all: rmdb dsrun

.PHONY: rmdb
rmdb:
	rm db.sqlite

.PHONY: srun
srun:
	python server.py

dsrun:
	DEBUG=true python server.py
