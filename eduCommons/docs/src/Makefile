# Makefile for eduCommons Documentation

PYTHON=/usr/local/bin/python
RST2HTML=/usr/local/bin/rst2html.py
RST2LATEX=/usr/local/bin/rst2latex.py
LATEX=/usr/bin/latex
DVIPDF=/usr/bin/dvipdf
HTMLDOCS=../INSTALL.html ../CHANGES.html ../MIGRATION.html ../MIGRATIONS_OLD.html ../IMSContentPackaging.html ../LOCALIZATION.html ../SETUP.html ../PORTLETS.html
STYLESHEET=./default.css
PDFDOCS=../INSTALL.pdf ../CHANGES.pdf ../MIGRATION.pdf ../MIGRATIONS_OLD.pdf ../IMSContentPackaging.pdf ../LOCALIZATION.pdf ../SETUP.pdf ../PORTLETS.pdf
TEXTDOCS=../INSTALL.txt ../CHANGES.txt ../MIGRATION.txt ../MIGRATIONS_OLD.txt ../IMSContentPackaging.txt ../LOCALIZATION.txt ../SETUP.txt ../PORTLETS.txt

all: htmldocs pdfdocs

htmldocs: $(HTMLDOCS) ../$(STYLESHEET)

pdfdocs: $(PDFDOCS)

textdocs: $(TEXTDOCS)

install: $(TEXTDOCS)
	mv ../*.txt ../../.
	

../%.pdf: %.dvi
	$(DVIPDF) $< $@

%.dvi: %.tex
	$(LATEX) $<
	$(LATEX) $<

%.tex: ../%.txt
	$(RST2LATEX) $< $@

../%.html: ../%.txt ../$(STYLESHEET)
	$(RST2HTML) --stylesheet=$(STYLESHEET) $< $@

../%.css: %.css
	cp $< ../.

../%.txt: %.txt
	cp $< ../.
	$(PYTHON) makedocs.py $@

clean:
	-rm ../*.pdf ../*.html ../*.css ../*.txt ../*.out
	-rm *.log *.aux *~ *.out
