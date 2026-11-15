CC = gcc
CFLAGS = -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Werror -pthread -O2 -g

SRCS = main.c barrier.c solver.c
TARGET = birthday-boy

all: $(TARGET)

$(TARGET): $(SRCS) bellman_ford.h
	$(CC) $(CFLAGS) -o $(TARGET) $(SRCS)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET) *.o

.PHONY: all run clean
