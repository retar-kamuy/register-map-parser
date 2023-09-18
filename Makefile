VENV = .venv/Scripts
PYTHON = $(VENV)/python
PIP = $(VENV)/pip

MODULE = excel2csv

freeze: requirements.txt
requirements.txt:
	$(PIP) freeze > $@

build:
	$(PYTHON) -m $(MODULE)