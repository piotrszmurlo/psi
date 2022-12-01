#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

int createSocket() {
    int socketfd = socket(AF_INET, SOCK_DGRAM, 0);

    if (socketfd == -1) {
        perror("Socket opening failure");
        exit(EXIT_FAILURE);
    }
    return socketfd;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Arguments: [IP address] [port]");
        exit(-1);
    }

    struct sockaddr_in servaddr;
    struct hostent *hp;
    memset(&servaddr, 0, sizeof(servaddr));

    hp = gethostbyname(argv[1]);
    if (hp == (struct hostent *) 0) {
        fprintf(stderr, "%s: unknown host\n", argv[1]);
        exit(2);
    }
    memcpy((char *) &servaddr.sin_addr, (char *) hp->h_addr,
           hp->h_length);
    char *data[] = {"datagram one", "datagram two", "datagram three"};
    servaddr.sin_port = htons(atoi(argv[2]));
    servaddr.sin_family = AF_INET;
    int socketfd = createSocket();
    int i;
    for (i = 0; i < 3; ++i) {
        sendto(socketfd, (const char *) data[i], strlen(data[i]), 0, (const struct sockaddr *) &servaddr,
               sizeof(servaddr));
        printf("message #%d sent\n", i + 1);
    }

    printf("Client quitting");
    close(socketfd);
    return 0;
}
