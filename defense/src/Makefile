NAME=presentation

.PHONY: all pdf clean clean-all

all: clean-all $(NAME).pdf

pdf: all
	make clean

$(NAME).pdf: $(NAME).tex
	pdflatex $<
	pdflatex $<

clean:
	rm -f $(NAME).dvi $(NAME).log $(NAME).blg $(NAME).bbl $(NAME).toc $(NAME).aux $(NAME).out $(NAME).lof $(NAME).ptc $(NAME).nav $(NAME).snm *.te~

clean-all: clean
	rm -f $(NAME).pdf
