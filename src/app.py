# File: src/app.py
"""
Flask application entry point for Project Gutenberg scraper
"""
from flask import Flask, render_template, request, jsonify, send_file
import json
import logging
import os
from utils import load_config, setup_logging
from scraper import GutenbergScraper
from pdf_generator import PDFGenerator
import tempfile
import threading

# This tells Flask to sgo UP one level from 'src' to find the folders.
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Global variables
config = None
scraper = None

def initialize_app():
    """Initialize application with configuration"""
    global config, scraper
    config = load_config()
    setup_logging()
    scraper = GutenbergScraper(config['subject_url'])

@app.route('/')
def index():
    """Main page with book list"""
    # Ensure app is initialized
    if scraper is None:
        initialize_app()
    
    try:
        page = request.args.get('page', 1, type=int)
        books, total_pages, has_next, has_prev = scraper.get_books_paginated(page, 25)
        
        # Correct path for render_template, no 'templates/' prefix needed
        return render_template('index.html', 
                             books=books,
                             current_page=page,
                             total_pages=total_pages,
                             has_next=has_next,
                             has_prev=has_prev,
                             config=config)
    except Exception as e:
        logging.error(f"Error loading main page: {str(e)}")
        # Correct path for render_template
        return render_template('index.html', 
                             books=[], 
                             error="Error loading books. Please try again.",
                             config=config)

@app.route('/api/validate_selection', methods=['POST'])
def validate_selection():
    """Validate book selection against constraints"""
    # Ensure app is initialized
    if scraper is None:
        initialize_app()
        
    try:
        selected_ids = request.json.get('selected_ids', [])
        
        if not selected_ids:
            return jsonify({'valid': False, 'reason': 'No books selected'})
        
        if len(selected_ids) > 10:
            return jsonify({'valid': False, 'reason': 'Maximum 10 books allowed'})
        
        # Get word count estimate
        total_words = scraper.estimate_total_words(selected_ids)
        if total_words > 10000:
            return jsonify({'valid': False, 'reason': f'Total estimated words ({total_words:,}) exceeds 10,000 limit'})
        
        return jsonify({
            'valid': True, 
            'book_count': len(selected_ids),
            'estimated_words': total_words
        })
    
    except Exception as e:
        logging.error(f"Error validating selection: {str(e)}")
        return jsonify({'valid': False, 'reason': 'Validation error'})

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF from selected books"""
    # Ensure app is initialized
    if scraper is None:
        initialize_app()
        
    try:
        selected_ids = request.json.get('selected_ids', [])
        filename = request.json.get('filename', 'gutenberg_books.pdf')
        
        if not selected_ids:
            return jsonify({'error': 'No books selected'}), 400
        
        # Generate PDF
        pdf_generator = PDFGenerator(config)
        temp_path = pdf_generator.create_pdf(scraper, selected_ids, filename)
        
        return send_file(temp_path, 
                        as_attachment=True, 
                        download_name=filename,
                        mimetype='application/pdf')
    
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': 'Failed to generate PDF'}), 500

if __name__ == '__main__':
    initialize_app()
    app.run(host='0.0.0.0', port=config['port'], debug=True)