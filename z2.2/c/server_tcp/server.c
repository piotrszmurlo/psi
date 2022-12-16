#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdbool.h>

#define BUFFER_SIZE 1024
#define PORT 53290
#define BACKLOG 5

bool moreWork();

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
    struct sockaddr_in servaddr;

    sockfd = createSocket();
    memset(&servaddr, 0, sizeof(servaddr));

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(PORT);

    bindSocket(sockfd);

    if ((listen(sockfd, BACKLOG)) != 0) {
        printf("listen() failure\n");
        exit(EXIT_FAILURE);
    }
    do {
        char buffer[BUFFER_SIZE] = {0};

        connection = accept(sockfd, (struct sockaddr *) 0, (int *) 0);
        if (connection < 0) {
            printf("accept() failure\n");
        } else {
            int n = recv(connection, buffer, BUFFER_SIZE, 0);
            if (n < 0) {
                printf("send() error\n");
            }
            printf("Length of the message: %d\n", n);
            printf("Received message: %s\n", buffer);
            char* data = "received, thanks";

            n = send(connection, data, strlen(data), 0);
            if (n < 0) {
                printf("send() error\n");
                exit(EXIT_FAILURE);
            }
        }
    } while (moreWork());
}

bool moreWork() {
    return 1;
}
