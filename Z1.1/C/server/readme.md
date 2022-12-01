## Z 1
### uruchomienie serwera:

$ docker build -t z16_server .

$ docker run -it --network-alias server1 --network z16_network --name server1 z16_server