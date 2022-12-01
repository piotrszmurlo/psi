#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define BUFFER_SIZE 1024

int createSocket() {
    int socketfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (socketfd == -1) {
        perror("Socket opening failure");
        exit(EXIT_FAILURE);
    }
    return socketfd;
}

int bindSocket(int socketfd) {
    struct sockaddr_in name;
    memset((char *) &name, 0, sizeof(name));
    name.sin_addr.s_addr = htonl(INADDR_ANY);
    name.sin_port = htons(0);
    name.sin_family = AF_INET;

    int bindRetVal = bind(socketfd, (const struct sockaddr *) &name, sizeof(name));

    if (bindRetVal == -1) {
        perror("Socket binding failure");
        exit(EXIT_FAILURE);
    }
    int len = sizeof(name);

    if (getsockname(socketfd, (struct sockaddr *) &name, &len) == -1) {
        perror("getting socket name failure");
        exit(1);
    }
    printf("Socket port #%d\n", ntohs(name.sin_port));
    return bindRetVal;
}

int main() {
    char buffer[BUFFER_SIZE] = {0};
    struct sockaddr_in cliaddr;
    memset((char *) &cliaddr, 0, sizeof(cliaddr));
    int socketfd = createSocket();
    bindSocket(socketfd);

    printf("Server started\n");
    int len = sizeof(cliaddr);
    while (1) {
        int n = recvfrom(socketfd, (char *) buffer, BUFFER_SIZE, 0, (struct sockaddr *) &cliaddr, &len);
        buffer[n] = '\0';
        printf("Client: %s\n", buffer);
    }
}
