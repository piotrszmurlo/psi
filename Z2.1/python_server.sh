#!/bin/bash
docker build -t z16_server python/server_tcp/
docker run -it --network-alias server1 --network z16_network --name server1 z16_server_py
