#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
all:
	mvn package

run:
	java -cp target/my-app-1.0-SNAPSHOT.jar com.mycompany.app.App

jail:
	./run_jail.sh /usr/lib/jvm/java-11-openjdk-amd64/bin/java -cp target/my-app-1.0-SNAPSHOT.jar com.mycompany.app.App

