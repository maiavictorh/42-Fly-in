VENV = .venv
PIP = $(VENV)/bin/pip
P3 = $(VENV)/bin/python3
FLAKE8 = $(VENV)/bin/flake8
MYPY = $(VENV)/bin/mypy
RM = rm -rf

MAIN = main.py

run: .venv
	clear
	$(P3) $(MAIN)

.venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install: .venv

debug:
	$(P3) -m pdb $(MAIN)

clean:
	$(RM) .mypy_cache
	$(RM) .idea
	$(RM) .vscode
	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	$(RM) $(VENV)

re: fclean install run

lint:
	$(FLAKE8) . --exclude $(VENV)
	$(MYPY) . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(FLAKE8) . --exclude $(VENV)
	$(MYPY) . --strict

.PHONY: run install debug clean fclean re lint lint-strict