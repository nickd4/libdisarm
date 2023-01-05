#!/bin/sh
./bootstrap
./configure CFLAGS="-static"
make LDFLAGS="-all-static"
