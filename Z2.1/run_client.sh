#!/bin/bash
docker build -t z16_client client_tcp/
docker run -it --network z16_network z16_client server1