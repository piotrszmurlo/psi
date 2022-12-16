#include <stdio.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#define BUFFER_SIZE 10
#define PORT 53290
#define BACKLOG 5


int createSocket() {
    int socketfd = socket(AF_INET, SOCK_STREAM, 0);
    if (socketfd == -1) {
        perror("Socket opening failure\n");
        exit(EXIT_FAILURE);
    }
    return socketfd;
}

void bindSocket(int socketfd) {
    struct sockaddr_in name;
    memset((char *) &name, 0, sizeof(name));
    name.sin_addr.s_addr = htonl(INADDR_ANY);
    name.sin_port = htons(PORT);
    name.sin_family = AF_INET;

    int bindRetVal = bind(socketfd, (const struct sockaddr *) &name, sizeof(name));

    if (bindRetVal == -1) {
        perror("Socket binding failure\n");
        exit(EXIT_FAILURE);
    }
    int len = sizeof(name);

    if (getsockname(socketfd, (struct sockaddr *) &name, &len) == -1) {
        perror("getting socket name failure\n");
        exit(1);
    }
    printf("Socket port #%d\n", ntohs(name.sin_port));
}

int main() {
    int sockfd, connection, len;
    struct sockaddr_in servaddr, cliaddr;
    int rval=0, i, nfds, nactive;

    sockfd = createSocket();
    nfds = sockfd + 1;
    memset(&servaddr, 0, sizeof(servaddr));

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(PORT);

    bindSocket(sockfd);

    if ((listen(sockfd, BACKLOG)) != 0) {
        printf("listen() failure\n");
        exit(EXIT_FAILURE);
    }

    len = sizeof(cliaddr);
    connection = accept(sockfd, (struct sockaddr*)&cliaddr, &len);

    if (connection < 0) {
        printf("server accept failed\n");
        exit(0);
    }
    else {
        printf("server accept the client\n");
    }
    for (;;) {
        char* buffer = (char*)malloc(BUFFER_SIZE);
        int n;

        bzero(buffer, BUFFER_SIZE);

        read(connection, buffer, BUFFER_SIZE);

        printf("From client: %s\t To client : ", buffer);
        bzero(buffer, BUFFER_SIZE);
        n = 0;

        while ((buffer[n++] = getchar()) != '\n')
            ;

        write(connection, buffer, sizeof(buffer));

        if (strncmp("exit", buffer, 4) == 0) {
            printf("Server Exit...\n");
            break;
        }

    }

    close(sockfd);
}
