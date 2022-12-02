#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

typedef struct datagram datagram;

int createSocket() {
    int socketfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (socketfd == -1) {
        printf("Socket opening failure");
        exit(EXIT_FAILURE);
    }
    return socketfd;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Arguments: [Server name] [port]\n");
        exit(-1);
    }
    struct hostent *hp;
    hp = gethostbyname(argv[1]);
    if (hp == (struct hostent *) 0) {
        printf("%s: unknown host\n", argv[1]);
        exit(2);
    }
    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    memcpy((char *) &servaddr.sin_addr, (char *) hp->h_addr,
           hp->h_length);
    servaddr.sin_port = htons(atoi(argv[2]));
    servaddr.sin_family = AF_INET;


    struct datagram {
        long a;
        int b;
        short c;
        char d[10];
    } data;
    data.a = 15;
    data.b = 3;
    data.c = 20;
    strcpy(data.d, "abcdefghi");

    int socketfd = createSocket();
    int i;
    sendto(socketfd, (const char *) &data, sizeof(struct datagram), 0, (const struct sockaddr *) &servaddr, sizeof(servaddr));
    printf("struct sent: \n{\n\ta:15\n\tb:3\n\tc:20\n\td:abcdefghi\n}\n");
    printf("Client quitting\n");
    close(socketfd);
    exit(0);
}
