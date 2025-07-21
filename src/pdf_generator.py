# File: src/pdf_generator.py
"""
PDF generation functionality
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import tempfile
import os
import logging

class PDFGenerator:
    def __init__(self, config):
        self.config = config
        self.font = config.get('font', 'Helvetica')
        self.font_color = config.get('font_color', '#800000')
        
    def create_pdf(self, scraper, book_ids, filename):
        """Create PDF with selected books"""
        try:
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                temp_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build story (content)
            story = []
            styles = self._create_styles()
            
            for i, book_id in enumerate(book_ids):
                if i > 0:
                    # Add page break between books
                    story.append(PageBreak())
                
                # Add book section
                self._add_book_section(story, scraper, book_id, styles)
            
            # Build PDF
            doc.build(story)
            
            return temp_path
            
        except Exception as e:
            logging.error(f"Error creating PDF: {str(e)}")
            raise
    
    def _create_styles(self):
        """Create paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Convert hex color to RGB
        color = self._hex_to_rgb(self.font_color)
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            fontName=self.font,
            textColor=color,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        
        # Author style
        author_style = ParagraphStyle(
            'CustomAuthor',
            parent=styles['Normal'],
            fontSize=12,
            fontName=self.font,
            textColor=color,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # Body style
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            fontName=self.font,
            textColor=color,
            alignment=TA_LEFT,
            spaceAfter=6
        )
        
        return {
            'title': title_style,
            'author': author_style,
            'body': body_style
        }
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        try:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
        except:
            return (0.5, 0, 0)  # Default maroon
    
    def _add_book_section(self, story, scraper, book_id, styles):
        """Add a book section to the PDF"""
        try:
            # Get book metadata
            books = scraper._fetch_all_books()
            book_info = None
            for book in books:
                if book['id'] == book_id:
                    book_info = book
                    break
            
            if not book_info:
                story.append(Paragraph(f"Error: Book {book_id} not found", styles['body']))
                return
            
            # Add section title page
            story.append(Paragraph(book_info['title'], styles['title']))
            story.append(Paragraph(f"by {book_info['author']}", styles['author']))
            
            # Add excerpt if available (first 500 words)
            content = scraper.get_book_content(book_id)
            if content and not content.startswith("Error:"):
                # Get excerpt
                words = content.split()[:500]
                excerpt = " ".join(words)
                if len(words) == 500:
                    excerpt += "..."
                
                story.append(Paragraph("Excerpt:", styles['author']))
                story.append(Spacer(1, 12))
                
                # Split into paragraphs for better formatting
                paragraphs = excerpt.split('\n\n')
                for para in paragraphs[:5]:  # Limit to first 5 paragraphs
                    if para.strip():
                        story.append(Paragraph(para.strip(), styles['body']))
                        story.append(Spacer(1, 6))
            else:
                story.append(Paragraph("Content unavailable", styles['body']))
            
            # Add separator (thick black line)
            story.append(Spacer(1, 20))
            line_table = Table([[''], ['']], colWidths=[6*inch], rowHeights=[0.05*inch, 0.05*inch])
            line_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.black),
                ('BACKGROUND', (0, 1), (0, 1), colors.white),
            ]))
            story.append(line_table)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            logging.error(f"Error adding book section for {book_id}: {str(e)}")
            story.append(Paragraph(f"Error processing book {book_id}", styles['body']))
