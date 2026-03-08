PYTHON ?= python3
VERSION ?= main
TARGET ?= .
REPO ?= https://github.com/guardiafinance/ahrena
PLATFORM ?=
LANGUAGE ?=
DIRECTIVES ?=
CLADES ?=

ifeq ($(OS),Windows_NT)
    PYTHON := python
endif

# URL for downloading install.py from GitHub Releases
ifeq ($(VERSION),main)
    BOOTSTRAP_URL = $(REPO)/releases/latest/download/install.py
else
    BOOTSTRAP_URL = $(REPO)/releases/download/$(VERSION)/install.py
endif

# Cross-platform download and cleanup commands
ifeq ($(OS),Windows_NT)
    DOWNLOAD_INSTALLER = powershell -Command "Invoke-WebRequest '$(BOOTSTRAP_URL)' -OutFile '.ahrena-bootstrap.py'"
    RM_BOOTSTRAP = powershell -Command "Remove-Item -Force '.ahrena-bootstrap.py' -ErrorAction SilentlyContinue"
else
    DOWNLOAD_INSTALLER = curl -sSL "$(BOOTSTRAP_URL)" -o .ahrena-bootstrap.py
    RM_BOOTSTRAP = rm -f .ahrena-bootstrap.py
endif

# Shared flags
SHARED_FLAGS = --target $(TARGET) --version $(VERSION) --repo $(REPO)
ifdef PLATFORM
    SHARED_FLAGS += --platform $(PLATFORM)
endif
ifdef LANGUAGE
    SHARED_FLAGS += --language $(LANGUAGE)
endif
ifdef DIRECTIVES
    SHARED_FLAGS += --directives $(DIRECTIVES)
endif
ifdef CLADES
    SHARED_FLAGS += --clades $(CLADES)
endif

BOOTSTRAP_CMD   = $(PYTHON) .ahrena-bootstrap.py $(SHARED_FLAGS)
INSTALL_CMD     = $(PYTHON) .ahrena/install.py $(SHARED_FLAGS)
DEV_INSTALL_CMD = $(PYTHON) scripts/install.py --local $(SHARED_FLAGS)

.PHONY: bootstrap install dev-install update uninstall clean help

help:
	@echo "Ahrena: AI-First Capability Framework"
	@echo ""
	@echo "Targets:"
	@echo "  bootstrap     First install (downloads installer from GitHub Release)"
	@echo "  install       Reinstall from local .ahrena/install.py"
	@echo "  dev-install   Install from local source (for framework development)"
	@echo "  update        Update to latest version (auto-detects platform)"
	@echo "  uninstall     Remove Ahrena with confirmation"
	@echo "  clean         Remove installed Ahrena files (no confirmation)"
	@echo ""
	@echo "Variables:"
	@echo "  PLATFORM     Target platform (e.g. cursor)"
	@echo "  VERSION      Tag or branch (default: main)"
	@echo "  TARGET       Target project path (default: .)"
	@echo "  REPO         GitHub repo URL"
	@echo "  LANGUAGE     Override default language (e.g. pt-BR, en, es)"
	@echo "  DIRECTIVES   Path or URL to custom .directives file"
	@echo "  CLADES       Comma-separated clades to install (default: all)"

bootstrap:
	$(DOWNLOAD_INSTALLER)
	$(BOOTSTRAP_CMD)
	$(RM_BOOTSTRAP)

install:
	$(INSTALL_CMD)

dev-install:
	$(DEV_INSTALL_CMD)

update:
	$(PYTHON) .ahrena/update.py --target $(TARGET) --version $(VERSION) --repo $(REPO)

uninstall:
	$(PYTHON) .ahrena/uninstall.py --target $(TARGET)

clean:
	$(PYTHON) .ahrena/install.py --target $(TARGET) --clean
