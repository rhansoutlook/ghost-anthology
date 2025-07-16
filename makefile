# Makefile for Ghost Story Anthology Project

VENV_NAME = ghost-anthology
PYTHON = $(VENV_NAME)/bin/python
PIP = $(VENV_NAME)/bin/pip
FLASK = $(VENV_NAME)/bin/flask

# --------------------------------------
# SETUP: Create virtual environment and install requirements
# --------------------------------------
setup:
	@echo "🔧 Creating virtual environment..."
	python3 -m venv $(VENV_NAME)
	@echo "📦 Installing Python dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Setup complete."

# --------------------------------------
# RUN: Start the Flask app locally
# --------------------------------------
run:
	@echo "🚀 Starting Flask app at http://127.0.0.1:5000 ..."
	PYTHONPATH=src FLASK_APP=src.app $(FLASK) run --port=5000

# --------------------------------------
# CLEAN: Remove Python bytecode and logs
# --------------------------------------
clean:
	find . -name '__pycache__' -exec rm -r {} +
	find . -name '*.pyc' -delete
	rm -f error.log

# --------------------------------------
# RESET: Remove venv and clean project
# --------------------------------------
reset:
	rm -rf $(VENV_NAME)
	make clean

# --------------------------------------
# GIT-CLEAN: Clean project artifacts, but KEEP venv
# --------------------------------------
git-clean:
	find . -name '__pycache__' -exec rm -r {} +
	find . -name '*.pyc' -delete
	rm -f error.log

# --------------------------------------
# HELP: Show available targets
# --------------------------------------
help:
	@echo "🛠️  Available Makefile targets:"
	@echo "  setup      – Create venv and install requirements"
	@echo "  run        – Start Flask app (http://localhost:5000)"
	@echo "  clean      – Remove .pyc, __pycache__, and logs"
	@echo "  reset      – Remove venv and clean project"
	@echo "  git-clean  – Clean repo artifacts, KEEP venv"
	@echo "  help       – Show this help message"
