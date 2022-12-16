#!/bin/bash
docker build -t z16_client_c c/client_tcp/
docker run -it --network z16_network z16_client_c server1