# File: Makefile
.PHONY: setup run clean

# Setup the application
setup:
	@echo "Setting up Project Gutenberg Scraper..."
	@python -m pip install --upgrade pip
	@pip install -r requirements.txt
	@echo "Setup complete!"

# Run the application
run:
	@echo "Starting Project Gutenberg Scraper..."
	@python src/app.py

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -f error.log
	@echo "Clean complete!"

# Install and run (convenience target)
install-and-run: setup run

# Help
help:
	@echo "Available targets:"
	@echo "  setup          - Install dependencies"
	@echo "  run            - Run the application"
	@echo "  clean          - Remove temporary files"
	@echo "  install-and-run - Setup and run in one command"
	@echo "  help           - Show this help"
