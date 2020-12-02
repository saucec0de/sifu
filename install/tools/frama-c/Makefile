all:
	podman build -t framac .

root:
	podman run --rm -it --entrypoint=/usr/bin/bash -v ${PWD}:/src -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=${DISPLAY} framac

run:
	podman run --rm -v ${PWD}:/src framac bash -l -c "frama-c -rte -eva test.c"

save:
	podman save framac -o framac_21_1.tar
	bzip2 framac_21_1.tar

# According to the idea from Thomas - start Container in detached mode :-)
start:
	podman run --rm -it --entrypoint=/usr/bin/bash -d -v ${PWD}:/src -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=${DISPLAY} --name framac_run framac

stop:
	podman stop -t0 framac_run

run2:
	podman exec -it framac_run bash -l -c "frama-c -rte -eva test.c"

gui:
	xhost +
	podman exec -it framac_run bash -l -c "frama-c-gui -rte -eva test.c"
