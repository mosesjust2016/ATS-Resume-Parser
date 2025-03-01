import json
import os
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash, session
from pypdf import PdfReader
from resumeparser import ats_extractor
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from urllib.parse import quote

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages

# Ensure the upload and output directories exist
UPLOAD_PATH = "__DATA__"
OUTPUT_PATH = "__OUTPUT__"
for path in [UPLOAD_PATH, OUTPUT_PATH]:
    if not os.path.exists(path):
        os.makedirs(path)

# Define resume templates (functions or configurations)
def template_basic(json_data, output_filename):
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Basic two-column layout similar to Angela's resume
    contact_info = []
    if "Full Name" in json_data and json_data["Full Name"]:
        contact_info.append(Paragraph(f"<font size=16><b>{json_data['Full Name']}</b></font>", styles['Normal']))
    if "Email" in json_data and json_data["Email"]:
        contact_info.append(Paragraph(f"✉ {json_data['Email']}", styles['Normal']))
    if "Phone" in json_data and json_data["Phone"]:
        contact_info.append(Paragraph(f"☎ {json_data['Phone']}", styles['Normal']))
    if "GitHub Profile" in json_data and json_data["GitHub Profile"]:
        contact_info.append(Paragraph(f"🌐 GitHub: {json_data['GitHub Profile']}", styles['Normal']))
    if "LinkedIn Profile" in json_data and json_data["LinkedIn Profile"]:
        contact_info.append(Paragraph(f"🔗 LinkedIn: {json_data['LinkedIn Profile']}", styles['Normal']))

    header_table = Table([
        [Paragraph("<font size=14><b>ADMINISTRATIVE ASSISTANT</b></font>", styles['Normal'])],
        [Table([[contact] for contact in contact_info], colWidths=[300], rowHeights=[20] * len(contact_info))]
    ], colWidths=[200, 300], rowHeights=[max(30, 20 * len(contact_info))])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))

    sections = [
        ("Employment History", "Employment History", lambda x: [item for job in x if isinstance(job, dict) for item in [
            Paragraph(f"<b>{str(job.get('Job Title', ''))} at {str(job.get('Company', ''))} - {str(job.get('Dates', ''))}</b>", styles['Heading3']),
            Paragraph(str(job.get('Description', '')), styles['Normal'])
        ]] if isinstance(x, list) else []),
        ("Technical Skills", "Technical Skills", lambda x: ListFlowable([Paragraph(str(skill), styles['Normal']) for skill in x if isinstance(skill, str)], bulletType='bullet') if isinstance(x, list) else []),
        ("Soft Skills", "Soft Skills", lambda x: ListFlowable([Paragraph(str(skill), styles['Normal']) for skill in x if isinstance(skill, str)], bulletType='bullet') if isinstance(x, list) else []),
        ("Education", "Education", lambda x: [item for edu in x if isinstance(edu, dict) for item in [
            Paragraph(f"<b>{str(edu.get('Degree', ''))} - {str(edu.get('Institution', ''))}, {str(edu.get('Location', ''))} ({str(edu.get('Dates', ''))})</b>", styles['Heading3']),
            Paragraph(str(edu.get('Achievements', '')), styles['Normal'])
        ]] if isinstance(x, list) else []),
        ("Certifications", "Certifications", lambda x: ListFlowable([Paragraph(str(cert), styles['Normal']) for cert in x if isinstance(cert, str)], bulletType='bullet') if isinstance(x, list) else []),
        ("Awards", "Awards", lambda x: ListFlowable([Paragraph(str(award), styles['Normal']) for award in x if isinstance(award, str)], bulletType='bullet') if isinstance(x, list) else []),
    ]

    for display_name, key, formatter in sections:
        if key in json_data:
            story.append(Paragraph(display_name, styles['Heading2']))
            content = formatter(json_data[key])
            if isinstance(content, list):
                for item in content:
                    story.append(item)
                    story.append(Spacer(1, 6))
            else:
                story.append(content)
                story.append(Spacer(1, 12))

    doc.build(story)

def template_modern(json_data, output_filename):
    # Similar to template_basic but with different styling (e.g., larger fonts, different spacing)
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    contact_info = []
    if "Full Name" in json_data and json_data["Full Name"]:
        contact_info.append(Paragraph(f"<font size=18><b>{json_data['Full Name']}</b></font>", styles['Normal']))
    if "Email" in json_data and json_data["Email"]:
        contact_info.append(Paragraph(f"✉ {json_data['Email']}", styles['Normal']))
    # Add other contact info (Phone, GitHub, LinkedIn) similarly

    header_table = Table([
        [Paragraph("<font size=16><b>ADMINISTRATIVE ASSISTANT</b></font>", styles['Normal'])],
        [Table([[contact] for contact in contact_info], colWidths=[300], rowHeights=[20] * len(contact_info))]
    ], colWidths=[200, 300], rowHeights=[max(40, 20 * len(contact_info))])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 18))

    # Use the same sections as template_basic but adjust spacing or fonts
    sections = [
        ("Employment History", "Employment History", lambda x: [item for job in x if isinstance(job, dict) for item in [
            Paragraph(f"<b>{str(job.get('Job Title', ''))} at {str(job.get('Company', ''))} - {str(job.get('Dates', ''))}</b>", styles['Heading3']),
            Paragraph(str(job.get('Description', '')), styles['Normal'])
        ]] if isinstance(x, list) else []),
        ("Technical Skills", "Technical Skills", lambda x: ListFlowable([Paragraph(str(skill), styles['Normal']) for skill in x if isinstance(skill, str)], bulletType='bullet') if isinstance(x, list) else []),
        ("Soft Skills", "Soft Skills", lambda x: ListFlowable([Paragraph(str(skill), styles['Normal']) for skill in x if isinstance(skill, str)], bulletType='bullet') if isinstance(x, list) else []),
        ("Education", "Education", lambda x: [item for edu in x if isinstance(edu, dict) for item in [
            Paragraph(f"<b>{str(edu.get('Degree', ''))} - {str(edu.get('Institution', ''))}, {str(edu.get('Location', ''))} ({str(edu.get('Dates', ''))})</b>", styles['Heading3']),
            Paragraph(str(edu.get('Achievements', '')), styles['Normal'])
        ]] if isinstance(x, list) else []),
        ("Certifications", "Certifications", lambda x: ListFlowable([Paragraph(str(cert), styles['Normal']) for cert in x if isinstance(cert, str)], bulletType='bullet') if isinstance(x, list) else []),
        ("Awards", "Awards", lambda x: ListFlowable([Paragraph(str(award), styles['Normal']) for award in x if isinstance(award, str)], bulletType='bullet') if isinstance(x, list) else []),
    ]

    for display_name, key, formatter in sections:
        if key in json_data:
            story.append(Paragraph(display_name, styles['Heading2']))
            story.append(Spacer(1, 12))
            content = formatter(json_data[key])
            if isinstance(content, list):
                for item in content:
                    story.append(item)
                    story.append(Spacer(1, 12))
            else:
                story.append(content)
                story.append(Spacer(1, 18))

    doc.build(story)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/process", methods=["POST"])
def ats():
    if 'pdf_doc' not in request.files:
        flash("No file uploaded", "error")
        return redirect(url_for('index'))

    doc = request.files['pdf_doc']
    if not doc.filename.endswith('.pdf'):
        flash("Only PDF files are supported", "error")
        return redirect(url_for('index'))

    doc_path = os.path.join(UPLOAD_PATH, "file.pdf")
    try:
        doc.save(doc_path)
    except Exception as e:
        flash(f"Failed to save file: {e}", "error")
        return redirect(url_for('index'))

    try:
        data = _read_file_from_path(doc_path)
        print("Extracted PDF text:", repr(data))
    except Exception as e:
        flash(f"Failed to read PDF: {e}", "error")
        return redirect(url_for('index'))

    parsed_data = ats_extractor(data)
    print("Parsed data from ats_extractor:", parsed_data)
    
    if isinstance(parsed_data, dict) and "error" in parsed_data:
        flash(parsed_data["error"], "error")
        return redirect(url_for('index'))
    
    parsed_data_json = json.dumps(parsed_data)
    parsed_data_encoded = quote(parsed_data_json)
    return redirect(url_for('review', data=parsed_data_encoded))

@app.route('/review')
def review():
    from urllib.parse import unquote 
    parsed_data_encoded = request.args.get('data', None)
    if not parsed_data_encoded:
        flash("No resume data available", "error")
        return redirect(url_for('index'))
    
    try:
        parsed_data_str = unquote(parsed_data_encoded)
        print("Decoded data in /review:", repr(parsed_data_str))
        parsed_data = json.loads(parsed_data_str)
        print("Parsed data in /review:", parsed_data)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error in /review: {e}")
        flash("Invalid resume data", "error")
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error in /review: {e}")
        flash("An error occurred while processing resume data", "error")
        return redirect(url_for('index'))

    templates = [
        {'name': 'Basic', 'function': 'template_basic'},
        {'name': 'Modern', 'function': 'template_modern'},
    ]
    return render_template('review.html', data=parsed_data, templates=templates)

@app.route('/generate/<template>', methods=["POST"])
def generate(template):
    parsed_data_str = request.form.get('data')
    if not parsed_data_str:
        flash("No resume data provided", "error")
        return redirect(url_for('index'))
    
    print("Full parsed_data_str in /generate:", repr(parsed_data_str))
    
    try:
        parsed_data = json.loads(parsed_data_str)
        print("Parsed data in /generate:", parsed_data)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error in /generate: {e}")
        flash("Invalid resume data format", "error")
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error in /generate: {e}")
        flash("An error occurred while processing resume data", "error")
        return redirect(url_for('index'))

    template_map = {
        'template_basic': template_basic,
        'template_modern': template_modern
    }
    
    pdf_func = template_map.get(template)
    if not pdf_func:
        flash("Invalid template selected", "error")
        return redirect(url_for('review', data=quote(json.dumps(parsed_data))))

    pdf_output_path = os.path.join(OUTPUT_PATH, f"ats_resume_{template}.pdf")
    try:
        pdf_func(parsed_data, pdf_output_path)
        pdf_url = f"/output/ats_resume_{template}.pdf"
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        flash(f"Failed to generate PDF: {e}", "error")
        return redirect(url_for('review', data=quote(json.dumps(parsed_data))))

    flash("Resume generated successfully", "success")
    return redirect(url_for('index', pdf_url=pdf_url))


@app.route('/output/<filename>')
def serve_pdf(filename):
    return send_from_directory(OUTPUT_PATH, filename)

def _read_file_from_path(path):
    reader = PdfReader(path)
    data = ""
    for page_no in range(len(reader.pages)):
        page = reader.pages[page_no]
        text = page.extract_text()
        if text:
            data += text + " "
    return data.strip()

if __name__ == "__main__":
    app.run(port=8000, debug=True)