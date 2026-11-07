# traillab - build with: make        tests with: make test   (gcc, pthreads; run inside WSL)
CC ?= gcc
CFLAGS ?= -O3 -march=native -Wall -Wextra -Wno-unused-parameter -Wno-misleading-indentation -Wno-comment -pthread
SRC = src/traillab.c src/smc.c src/diff.c src/main.c
HDR = src/traillab.h src/smc.h src/diff.h

traillab: $(SRC) $(HDR)
	$(CC) $(CFLAGS) -o $@ $(SRC) -lm

test: traillab
	bash tests/known_answers.sh

quicktest: traillab
	QUICK=1 bash tests/known_answers.sh

clean:
	rm -f traillab
.PHONY: test quicktest clean
