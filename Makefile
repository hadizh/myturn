.PHONY: all venv clean

VENV := venv

all: venv

venv: requirements.txt
	python -m venv $(VENV)
	$(VENV)/Scripts/pip install -r requirements.txt

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
