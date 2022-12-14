#!/bin/bash
docker build -t z16_client python/client_tcp/
docker run -it --network z16_network z16_client_py server1