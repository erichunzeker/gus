CC = xelatex
SRC_DIR = src
SRCS = $(shell find $(DIR) -name '*.tex')
OUTPUT_DIR = output

report.pdf: report.tex $(SRCS)
	$(CC) -output-directory=$(OUTPUT_DIR) $<
