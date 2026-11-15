CC = gcc
CFLAGS = -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Werror -pthread -O2 -g

SRCS = main.c clock.c actors.c
TARGET = airport-troubles

all: $(TARGET)

$(TARGET): $(SRCS) airport.h
	$(CC) $(CFLAGS) -o $(TARGET) $(SRCS)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET) *.o

.PHONY: all run clean
