#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
run:
	FLASK_APP=sifu.py FLASK_ENV=development flask run

pack:
	git add .
	cd Deployment/Docker; make pack
	git add Deployment/Docker
	git commit -m "pack sifu"

clean:
	cd upload; make all
	./initUsers.py -x
	./initUsers.py -r
	rm -f access.log.csv sifu.log
