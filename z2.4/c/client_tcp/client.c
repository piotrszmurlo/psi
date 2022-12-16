#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <time.h>

#define PORT 53290
#define BUFFER_SIZE 1024
#define DATA_LOOP 100

int createSocket() {
    int socketfd = socket(AF_INET, SOCK_STREAM, 0);
    if (socketfd == -1) {
        printf("Socket opening failure\n");
        exit(EXIT_FAILURE);
    }
    return socketfd;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Arguments: [Server name]\n");
        exit(EXIT_FAILURE);
    }
    struct hostent *hp;
    hp = gethostbyname(argv[1]);
    if (hp == (struct hostent *) 0) {
        printf("%s: unknown host\n", argv[1]);
        exit(EXIT_FAILURE);
    }
    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    memcpy((char *) &servaddr.sin_addr, (char *) hp->h_addr,
           hp->h_length);
    servaddr.sin_port = htons(PORT);
    servaddr.sin_family = AF_INET;

    int socketfd = createSocket();

    int connection = connect(socketfd, (const struct sockaddr *) &servaddr, sizeof(servaddr));
    if (connection < 0) {
        printf("connect() failure\n");
        exit(EXIT_FAILURE);
    }
    char* data = "18\0abcdefghijklmnoprstuw";
    int i;
    clock_t start, end;
    double time_resullts[DATA_LOOP];
    double cpu_time_used;

    for(i=0; i<DATA_LOOP; i++) {
        start = clock();
        int n = send(socketfd, data, 21, 0);
        end = clock();
        cpu_time_used = ((double) (end - start)) / CLOCKS_PER_SEC;
        if (n < 0) {
            printf("send() error\n");
            printf("%d\n", h_errno);
            exit(EXIT_FAILURE);
        }
        time_resullts[i] = cpu_time_used;
        printf("Message sent after %f seconds.\n", cpu_time_used);
        char buffer[BUFFER_SIZE] = {0};
        n = recv(socketfd, buffer, BUFFER_SIZE, 0);
        if (n < 0) {
            printf("recv() error\n");
            printf("%d\n", h_errno);
            exit(EXIT_FAILURE);
        }
        printf("Received message from server: %s\n", buffer);
    }

    close(socketfd);
    exit(EXIT_SUCCESS);
}