#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate PDF from markdown using reportlab
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import os

def find_chinese_font():
    """Find available Chinese font"""
    font_paths = [
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/arphic/uming.ttc',
        '/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',
    ]
    for path in font_paths:
        if os.path.exists(path):
            return path
    return None

def parse_markdown(text):
    """Parse markdown and return list of (style, content) tuples"""
    lines = text.split('\n')
    elements = []
    in_code_block = False
    
    for line in lines:
        line = line.rstrip()
        
        # Code blocks
        if line.startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            elements.append(('code', line))
            continue
        
        # Headers
        if line.startswith('# '):
            elements.append(('h1', line[2:]))
        elif line.startswith('## '):
            elements.append(('h2', line[3:]))
        elif line.startswith('### '):
            elements.append(('h3', line[4:]))
        elif line.startswith('#### '):
            elements.append(('h4', line[5:]))
        elif line.startswith('---'):
            elements.append(('hr', ''))
        elif line.strip() == '':
            elements.append(('empty', ''))
        else:
            # Regular paragraph
            elements.append(('p', line))
    
    return elements

def clean_markdown(text):
    """Convert markdown formatting to reportlab markup"""
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
    # Remove markdown links, keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return text

def create_pdf(md_file, pdf_file):
    """Create PDF from markdown file"""
    
    # Find Chinese font
    font_path = find_chinese_font()
    if font_path:
        print(f"Using font: {font_path}")
        font_name = 'ChineseFont'
        pdfmetrics.registerFont(TTFont(font_name, font_path))
    else:
        print("No Chinese font found, using default")
        font_name = 'Helvetica'
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'Title',
        fontName=font_name,
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    
    # H2 style
    h2_style = ParagraphStyle(
        'Heading2',
        fontName=font_name,
        fontSize=16,
        leading=22,
        spaceBefore=20,
        spaceAfter=10,
        textColor='#333333',
    )
    
    # H3 style
    h3_style = ParagraphStyle(
        'Heading3',
        fontName=font_name,
        fontSize=14,
        leading=18,
        spaceBefore=15,
        spaceAfter=8,
        textColor='#444444',
    )
    
    # H4 style
    h4_style = ParagraphStyle(
        'Heading4',
        fontName=font_name,
        fontSize=12,
        leading=16,
        spaceBefore=10,
        spaceAfter=6,
        textColor='#555555',
    )
    
    # Normal paragraph style
    p_style = ParagraphStyle(
        'ChineseNormal',
        fontName=font_name,
        fontSize=11,
        leading=18,
        alignment=TA_JUSTIFY,
        spaceBefore=4,
        spaceAfter=4,
        firstLineIndent=22,  # First line indent for Chinese
    )
    
    # Metadata style (no indent)
    meta_style = ParagraphStyle(
        'Meta',
        fontName=font_name,
        fontSize=11,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=2,
        spaceAfter=2,
    )
    
    # Quote style
    quote_style = ParagraphStyle(
        'Quote',
        fontName=font_name,
        fontSize=10,
        leading=16,
        leftIndent=20,
        spaceBefore=6,
        spaceAfter=6,
        textColor='#666666',
    )
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    elements = parse_markdown(md_text)
    
    # Create PDF
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    
    story = []
    
    for style_name, content in elements:
        if style_name == 'h1':
            story.append(Paragraph(clean_markdown(content), title_style))
        elif style_name == 'h2':
            story.append(Paragraph(clean_markdown(content), h2_style))
        elif style_name == 'h3':
            story.append(Paragraph(clean_markdown(content), h3_style))
        elif style_name == 'h4':
            story.append(Paragraph(clean_markdown(content), h4_style))
        elif style_name == 'p':
            text = clean_markdown(content)
            if text.strip():
                # Check if it's metadata (starts with **)
                if text.startswith('<b>') and ':' in text:
                    story.append(Paragraph(text, meta_style))
                else:
                    story.append(Paragraph(text, p_style))
        elif style_name == 'empty':
            story.append(Spacer(1, 6))
        elif style_name == 'hr':
            story.append(Spacer(1, 12))
        elif style_name == 'code':
            story.append(Paragraph(content, quote_style))
    
    doc.build(story)
    print(f"PDF created: {pdf_file}")

if __name__ == '__main__':
    md_file = '/home/xmliao/.openclaw/workspace/书评_品三国.md'
    pdf_file = '/home/xmliao/文件/书评_品三国.pdf'
    create_pdf(md_file, pdf_file)