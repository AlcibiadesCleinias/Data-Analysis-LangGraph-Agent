.PHONY: install test lint run diagram clean

SHELL := /bin/bash
PYTHON ?= python3
VENV_DIR ?= venv
VENV_BIN := $(VENV_DIR)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

GOOGLE_APPLICATION_CREDENTIALS ?= $(shell pwd)/.secrets/bigquery-sa.json

$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PIP) install --upgrade pip setuptools wheel

install: $(VENV_PYTHON)
	$(VENV_PIP) install -r requirements.txt

test: install
	$(VENV_PYTHON) -m pytest

lint: install
	$(VENV_PYTHON) -m ruff check src tests || true

run: install
	@[ -f "$(GOOGLE_APPLICATION_CREDENTIALS)" ] || (echo "GOOGLE_APPLICATION_CREDENTIALS not found at $(GOOGLE_APPLICATION_CREDENTIALS)" && exit 1)
	@echo "Using GOOGLE_APPLICATION_CREDENTIALS=$(GOOGLE_APPLICATION_CREDENTIALS)"
	GOOGLE_APPLICATION_CREDENTIALS=$(GOOGLE_APPLICATION_CREDENTIALS) $(VENV_PYTHON) -m src.cli

diagram: install
	$(VENV_PYTHON) -m scripts.generate_flow_diagram

clean:
	rm -rf $(VENV_DIR)

