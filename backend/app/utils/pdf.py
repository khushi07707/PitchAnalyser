from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(report_data: dict) -> BytesIO:
    """
    Compiles detailed pitch assessment metrics into a beautiful, styled PDF document.
    Returns: BytesIO stream containing the compiled PDF.
    """
    buffer = BytesIO()
    
    # Page setup: letter format with 1/2 inch margins
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=36, 
        leftMargin=36, 
        topMargin=36, 
        bottomMargin=36
    )
    story = []
    
    # Styles config
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#0F172A'), # Slate 900
        spaceAfter=15,
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'DocSec',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1E293B'), # Slate 800
        spaceBefore=15,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#334155'), # Slate 700
        leading=14,
        spaceAfter=6
    )
    
    bold_body_style = ParagraphStyle(
        'DocBoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    # 1. Document Title Header
    story.append(Paragraph(f"Pitch Performance Analysis", title_style))
    story.append(Paragraph(f"<b>Recording Filename:</b> {report_data['filename']}", body_style))
    story.append(Paragraph(f"<b>Assessment Date:</b> {report_data['created_at']}", body_style))
    story.append(Spacer(1, 15))
    
    # 2. Score Summary Table
    story.append(Paragraph("Vocal & Communication Dimension Scores", section_style))
    data = [
        [Paragraph("<b>Performance Dimension</b>", bold_body_style), Paragraph("<b>Score (0-100)</b>", bold_body_style)],
        ["Speech Clarity", f"{report_data['clarity_score']}"],
        ["Speaker Confidence", f"{report_data['confidence_score']}"],
        ["Vocal Engagement", f"{report_data['engagement_score']}"],
        ["Communication Style", f"{report_data['communication_score']}"],
        ["Vocal Quality & Tone", f"{report_data['voice_quality_score']}"],
        ["OVERALL PITCH SCORE", f"{report_data['overall_score']}"]
    ]
    t = Table(data, colWidths=[240, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,1), (-1,-2), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#ECFDF5')), # Soft green highlight for overall score
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#065F46')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    
    # 3. Transcript
    story.append(Paragraph("Speech-to-Text Transcript", section_style))
    story.append(Paragraph(report_data['transcript'], body_style))
    story.append(Spacer(1, 10))
    
    # 4. Review Summary
    story.append(Paragraph("VC Evaluator Review", section_style))
    story.append(Paragraph(report_data['overall_review'], body_style))
    story.append(Spacer(1, 10))
    
    # 5. Strengths and Suggestions
    story.append(Paragraph("Key Strengths", section_style))
    for idx, strength in enumerate(report_data['strengths']):
        story.append(Paragraph(f"<b>{idx+1}.</b> {strength}", body_style))
        
    story.append(Paragraph("Weaknesses & Actionable Suggestions", section_style))
    for idx, (weakness, suggestion) in enumerate(zip(report_data['weaknesses'], report_data['suggestions'])):
        story.append(Paragraph(f"<b>{idx+1}. Concern:</b> {weakness}", body_style))
        story.append(Paragraph(f"   <b>Action:</b> {suggestion}", body_style))
        story.append(Spacer(1, 3))
        
    # Build document
    doc.build(story)
    buffer.seek(0)
    return buffer
