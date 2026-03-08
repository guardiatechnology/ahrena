PYTHON ?= python3
AHRENA_VERSION ?= main
AHRENA_TARGET ?= .
AHRENA_REPO ?= https://github.com/guardiafinance/ahrena
AHRENA_LANGUAGE ?=
AHRENA_DIRECTIVES ?=
AHRENA_CLADES ?=

ifeq ($(OS),Windows_NT)
    PYTHON := python
endif

INSTALL_CMD = $(PYTHON) .ahrena/install.py --target $(AHRENA_TARGET) --version $(AHRENA_VERSION) --repo $(AHRENA_REPO)
ifdef AHRENA_LANGUAGE
    INSTALL_CMD += --language $(AHRENA_LANGUAGE)
endif
ifdef AHRENA_DIRECTIVES
    INSTALL_CMD += --directives $(AHRENA_DIRECTIVES)
endif
ifdef AHRENA_CLADES
    INSTALL_CMD += --clades $(AHRENA_CLADES)
endif

.PHONY: install install-cursor update uninstall clean help

help:
	@echo "Ahrena: AI-First Capability Framework"
	@echo ""
	@echo "Targets:"
	@echo "  install          Install .ahrena/ only (framework + directives)"
	@echo "  install-cursor   Install .ahrena/ + generate .cursor/ files"
	@echo "  update           Update to latest version (auto-detects platform)"
	@echo "  uninstall        Remove Ahrena with confirmation"
	@echo "  clean            Remove installed Ahrena files (no confirmation)"
	@echo ""
	@echo "Variables:"
	@echo "  AHRENA_VERSION      Tag or branch (default: main)"
	@echo "  AHRENA_TARGET       Target project path (default: .)"
	@echo "  AHRENA_REPO         GitHub repo URL"
	@echo "  AHRENA_LANGUAGE     Override default language (e.g. pt-BR, en, es)"
	@echo "  AHRENA_DIRECTIVES   Path or URL to custom .directives file"
	@echo "  AHRENA_CLADES       Comma-separated clades to install (default: all)"

install:
	$(INSTALL_CMD)

install-cursor:
	$(INSTALL_CMD) --platform cursor

update:
	$(PYTHON) .ahrena/update.py --target $(AHRENA_TARGET) --version $(AHRENA_VERSION) --repo $(AHRENA_REPO)

uninstall:
	$(PYTHON) .ahrena/uninstall.py --target $(AHRENA_TARGET)

clean:
	$(PYTHON) .ahrena/install.py --target $(AHRENA_TARGET) --clean
