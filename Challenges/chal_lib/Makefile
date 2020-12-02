##################################################
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
##################################################

COMPILER ?= gcc

ifeq ($(COMPILER),gcc)
##############################
# gcc compiler configuration #
##############################
COPTS   ?= -fsanitize=address                    \
           -fsanitize=pointer-compare            \
           -fsanitize=pointer-subtract           \
           -fsanitize=leak                       \
           -fsanitize=undefined                  \
           -fsanitize=shift                      \
           -fsanitize=shift-exponent             \
           -fsanitize=shift-base                 \
           -fsanitize=integer-divide-by-zero     \
           -fsanitize=unreachable                \
           -fsanitize=vla-bound                  \
           -fsanitize=null                       \
           -fsanitize=return                     \
           -fsanitize=signed-integer-overflow    \
           -fsanitize=bounds                     \
           -fsanitize=bounds-strict              \
           -fsanitize=alignment                  \
           -fsanitize=object-size                \
           -fsanitize=float-divide-by-zero       \
           -fsanitize=float-cast-overflow        \
           -fsanitize=nonnull-attribute          \
           -fsanitize=returns-nonnull-attribute  \
           -fsanitize=bool                       \
           -fsanitize=enum                       \
           -fsanitize=vptr                       \
           -fsanitize=pointer-overflow           \
           -fsanitize=builtin                    \
           -fsanitize-address-use-after-scope    \
		   -fcf-protection=full -static-libasan
EXTRAOPTS   ?= -Werror=implicit-function-declaration -fstack-usage
CC           = gcc-10 -std=gnu11 -g 
CPPC         = g++-10 -std=gnu++11 -g

ifeq ($(M32),yes)
COPTS     += -m32
EXTRAOPTS += -m32
endif

else # ifeq(gcc)
################################
# clang compiler configuration #
################################
COPTS       ?= -std=c99 -g
EXTRAOPTS   ?=
CC           = clang-10
CPPC         = clang++-10
endif

################################
# Global Configuration
################################
ERRFILE     ?= stderr.txt
OUTFILE     ?= stdout.txt
COMPILEFILE ?= compile.txt
TIMEOUT     ?= 10s
M32         ?= no
REM_TEST    ?= yes
SPECIAL     ?= yes
FILES_C      = $(wildcard *.c)
FILES_CPP    = $(wildcard *.cpp)
FILES_O      = $(FILES_C:.c=.o) $(FILES_CPP:.cpp=.o)
MAKE         = make -s
RUN_MAIN     = ./run_jail.sh ./timeout $(TIMEOUT) ./main
# man terminal-colors.d
COLOR_RED    = \e[0;31m
COLOR_GREEN  = \e[0;32m
COLOR_YELLOW = \e[0;33m
COLOR_PURPLE = \e[0;35m
COLOR_WHITE  = \e[1;37m
COLOR_OFF    = \e[0m

.PHONY: all
all: run

.PHONY: run
run:
	@$(MAKE) clean
	@$(MAKE) inject
	@$(MAKE) compile
	@$(MAKE) jail
	@$(MAKE) analyse
	@$(MAKE) ai
	@echo "[$(COLOR_WHITE)RUN   $(COLOR_OFF) ]: RUN: done."

.PHONY: inject
inject:
	@echo Modifying/Injecting files in the project...
	@./inject.py || true

.PHONY: compile
compile:
	@echo Compiling the project...
	@$(MAKE) main

.PHONY: analyse
analyse:
	@./analyse.py || true
	@echo "[$(COLOR_PURPLE)ANALYSE$(COLOR_OFF)]: Analysis: done."

.PHONY: ai
ai:
	@./ai.py      || true 
	@echo "[$(COLOR_GREEN)AI    $(COLOR_OFF) ]: AI: done."

.PHONY: jail
jail:
	@mkdir -p sifu_results
	@cp `which timeout` .
	@$(RUN_MAIN) 2>> $(ERRFILE) >> $(OUTFILE) || true

.PHONY: main
main: $(FILES_O)
ifeq (,$(wildcard ./main.c))
	@echo "[$(COLOR_WHITE)COMPILE$(COLOR_OFF)]: Project Type: C++"
	@$(CPPC) $(COPTS) $(EXTRAOPTS) -o main $^ 2>> $(COMPILEFILE)   || true
else
	@echo "[$(COLOR_WHITE)COMPILE$(COLOR_OFF)]: Project Type: C"
	@$(CC) $(COPTS) $(EXTRAOPTS) -o main $^ 2>> $(COMPILEFILE)     || true
endif

#################################################
################ Special   Rules ################
#################################################
-include Makefile.special

#################################################
################ Fall-Back Rules ################
#################################################
.c.o:
ifeq (,$(wildcard ./main.c))
	@echo "[$(COLOR_YELLOW)COMPILE$(COLOR_OFF)]: Compiling C file (with C++ compiler): $^"
	@$(CPPC) $(EXTRAOPTS) -c $< -o $@ 2>> $(COMPILEFILE)                || true
	@$(CPPC) $(EXTRAOPTS) -c -S -masm=intel $< 2> /dev/null > /dev/null || true
	@$(CPPC) $(EXTRAOPTS) -fpreprocessed -dD -E $< > $<.pp 2> /dev/null || true
else
	@echo "[$(COLOR_YELLOW)COMPILE$(COLOR_OFF)]: Compiling C file: $^"
	@$(CC) $(COPTS) $(EXTRAOPTS) -c $< -o $@ 2>> $(COMPILEFILE)                || true
	@$(CC) $(COPTS) $(EXTRAOPTS) -c -S -masm=intel $< 2> /dev/null > /dev/null || true
	@$(CC) $(COPTS) $(EXTRAOPTS) -fpreprocessed -dD -E $< > $<.pp 2> /dev/null || true
endif

.cpp.o:
	@echo "[$(COLOR_YELLOW)COMPILE$(COLOR_OFF)]: Compiling C++ file: $^"
	@$(CPPC) $(COPTS) $(EXTRAOPTS) -c $< -o $@ 2>> $(COMPILEFILE)                || true
	@$(CPPC) $(COPTS) $(EXTRAOPTS) -c -S -masm=intel $< 2> /dev/null > /dev/null || true
	@$(CPPC) $(COPTS) $(EXTRAOPTS) -fpreprocessed -dD -E $< > $<.pp 2> /dev/null || true

.PHONY: basic_clean
basic_clean:
	@rm -rf main
	@rm -rf *.o
	@rm -rf *.s
	@rm -rf *.pp
	@rm -rf *.su

.PHONY: clean
clean:
	@$(MAKE) basic_clean
	@rm -rf __pycache__
	@rm -rf $(ERRFILE)
	@rm -rf $(OUTFILE)
	@rm -rf $(COMPILEFILE)
	@rm -rf x*.txt
	@rm -rf timeout
ifeq ($(REM_TEST),yes)
	@rm -rf sifu_results
endif
