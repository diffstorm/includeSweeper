CC = gcc
CFLAGS = -Wall -Wextra

SRCDIR = src
INCDIR = include
BUILDDIR = build
BINDIR = bin

TARGET = $(BINDIR)/main

SRCS = $(wildcard $(SRCDIR)/*.c)
OBJS = $(SRCS:$(SRCDIR)/%.c=$(BUILDDIR)/%.o)
DEPS = $(wildcard $(INCDIR)/*.h)

$(TARGET): $(OBJS)
	@mkdir -p $(BINDIR)
	$(CC) $(CFLAGS) -o $@ $^

$(BUILDDIR)/%.o: $(SRCDIR)/%.c $(DEPS)
	@mkdir -p $(BUILDDIR)
	$(CC) $(CFLAGS) -I$(INCDIR) -c -o $@ $<

.PHONY: clean

clean:
	rm -rf $(BUILDDIR) $(BINDIR)

