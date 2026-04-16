PYTHON ?= python3
VERSION ?= main
TARGET ?= .
REPO ?= https://github.com/guardiafinance/ahrena
PLATFORM ?=
LANGUAGE ?=
DIRECTIVES ?=
CLADES ?=
SOURCE ?=
LOCAL ?=

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

# Optional flags for install/update when using SOURCE or LOCAL (no --version --repo)
LOCAL_OPTS :=
ifdef PLATFORM
LOCAL_OPTS += --platform $(PLATFORM)
endif
ifdef LANGUAGE
LOCAL_OPTS += --language $(LANGUAGE)
endif
ifdef DIRECTIVES
LOCAL_OPTS += --directives $(DIRECTIVES)
endif
ifdef CLADES
LOCAL_OPTS += --clades $(CLADES)
endif

# Install: use SOURCE or LOCAL for local source, else remote
ifdef SOURCE
INSTALL_CMD_RUN = $(PYTHON) .ahrena/install.py --target $(TARGET) --source $(SOURCE) $(LOCAL_OPTS)
else
ifdef LOCAL
INSTALL_CMD_RUN = $(PYTHON) .ahrena/install.py --target $(TARGET) --local $(LOCAL_OPTS)
else
INSTALL_CMD_RUN = $(INSTALL_CMD)
endif
endif

# Update: use SOURCE or LOCAL for local source, else remote
ifdef SOURCE
UPDATE_CMD_RUN = $(PYTHON) .ahrena/update.py --target $(TARGET) --source $(SOURCE)
else
ifdef LOCAL
UPDATE_CMD_RUN = $(PYTHON) .ahrena/update.py --target $(TARGET) --local
else
UPDATE_CMD_RUN = $(PYTHON) .ahrena/update.py --target $(TARGET) --version $(VERSION) --repo $(REPO)
endif
endif

# Detect the directory of this Makefile (the Ahrena repo root).
# Used by install-to so --self resolves correctly regardless of CWD.
MAKEFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: bootstrap install dev-install install-to update sync-cursor sync-claude-code uninstall clean validate help

help:
	@echo "Ahrena: AI-First Capability Framework"
	@echo ""
	@echo "Targets:"
	@echo "  bootstrap     First install (downloads installer from GitHub Release)"
	@echo "  install       Reinstall from .ahrena/install.py (default: remote)"
	@echo "  dev-install   Install from local source (run from Ahrena repo root)"
	@echo "  install-to    Offline install FROM this repo TO any target (no network)"
	@echo "                  make install-to TARGET=/path/to/project PLATFORM=cursor"
	@echo "  update        Update installation (default: remote). After dev-install use update LOCAL=1 or SOURCE=..."
	@echo "  sync-cursor   Regenerate .cursor/ from .ahrena/framework/ and .ahrena/artifacts/ (no download)"
	@echo "  sync-claude-code  Regenerate .claude/ + CLAUDE.md from .ahrena/ (no download)"
	@echo "  uninstall     Remove Ahrena with confirmation"
	@echo "  clean         Remove installed Ahrena files (no confirmation)"
	@echo ""
	@echo "Variables:"
	@echo "  PLATFORM     Target platform (e.g. cursor, claude-code)"
	@echo "  VERSION      Tag or branch (default: main)"
	@echo "  TARGET       Target project path (default: .)"
	@echo "  REPO         GitHub repo URL"
	@echo "  SOURCE       Path to local Ahrena repo (install/update from local)"
	@echo "  LOCAL        If set (e.g. LOCAL=1), install/update from current dir as source"
	@echo "  LANGUAGE     Override default language (e.g. pt-BR, en, es)"
	@echo "  DIRECTIVES   Path or URL to custom .directives file"
	@echo "  CLADES       Comma-separated clades to install (default: all)"

bootstrap:
	$(DOWNLOAD_INSTALLER)
	$(BOOTSTRAP_CMD)
	$(RM_BOOTSTRAP)

install:
	$(INSTALL_CMD_RUN)

dev-install:
	$(DEV_INSTALL_CMD)

install-to:
	$(PYTHON) $(MAKEFILE_DIR)scripts/install.py --self --target $(TARGET) $(LOCAL_OPTS)

update:
	$(UPDATE_CMD_RUN)

sync-cursor:
	$(PYTHON) .ahrena/update.py --target $(TARGET) --sync-cursor

sync-claude-code:
	$(PYTHON) .ahrena/update.py --target $(TARGET) --sync-claude-code

uninstall:
	$(PYTHON) .ahrena/uninstall.py --target $(TARGET)

clean:
	$(PYTHON) .ahrena/install.py --target $(TARGET) --clean

validate:
	$(PYTHON) scripts/validate.py
