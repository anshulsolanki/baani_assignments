import time
import markdown
from fpdf import FPDF
import os
import re

def save_markdown_to_pdf(text, output_path, title="Analysis Report"):
    """
    Saves the markdown text as a beautified PDF file using fpdf2.
    Uses standard Helvetica font (ensure text contains only Latin-1 characters).
    """
    # Convert Markdown to HTML
    html_content = markdown.markdown(text, extensions=['tables'])
    
    # Inject spacing and basic styling into HTML tags
    html_content = html_content.replace("<p>", "<p style='margin-bottom: 10px; line-height: 1.6;'>")
    html_content = html_content.replace("<h1>", "<h1 style='color: #2c3e50; font-size: 18pt; margin-top: 20px; border-bottom: 1px solid #eee;'>")
    html_content = html_content.replace("<h2>", "<h2 style='color: #34495e; font-size: 14pt; margin-top: 15px;'>")
    html_content = html_content.replace("<h3>", "<h3 style='color: #7f8c8d; font-size: 12pt; margin-top: 10px;'>")
    html_content = html_content.replace("<ul>", "<ul style='margin-bottom: 10px;'>")
    html_content = html_content.replace("<li>", "<li style='margin-bottom: 5px;'>")

    # Table styling via regex
    html_content = re.sub(r'<table>', '<table border="1" width="100%" style="border-collapse: collapse;">', html_content)
    
    # Flatten Whitespace for tables
    html_content = html_content.replace("\n", "").replace("\r", "")

    # Safe Attribute Stripping
    html_content = re.sub(r'<th\b[^>]*>', '<th>', html_content)
    html_content = re.sub(r'<td\b[^>]*>', '<td>', html_content)
    
    # Inject Clean Styling for tables
    html_content = re.sub(r'<th>', '<th style="background-color: #f0f0f0; padding: 5px; font-weight: bold;">', html_content)
    html_content = re.sub(r'<td>', '<td style="padding: 5px;">', html_content)

    class PDF(FPDF):
        def header(self):
            self.set_font("helvetica", "B", 16)
            self.set_text_color(44, 62, 80)
            width = self.get_string_width(title) + 6
            self.set_x((210 - width) / 2)
            self.cell(width, 10, title, border=0, new_x="LMARGIN", new_y="NEXT", align="C")
            self.ln(5)
            self.set_draw_color(44, 62, 80)
            self.set_line_width(0.5)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            self.set_x(-50)
            self.cell(0, 10, timestamp, align="R")

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=11)
    pdf.set_text_color(51, 51, 51)
    
    try:
        pdf.write_html(html_content)
        pdf.output(output_path)
        print(f"PDF generated successfully at {output_path}")
    except Exception as e:
        print(f"PDF generation failed: {e}")
        # Fallback to plain text if HTML fails
        try:
            pdf = PDF()
            pdf.add_page()
            pdf.set_font("Courier", size=10)
            # Replace non-latin-1 chars with ? to avoid crashes
            safe_text = text.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, safe_text)
            pdf.output(output_path)
            print(f"Fallback PDF generated at {output_path}")
        except Exception as e2:
            print(f"All PDF generation attempts failed: {e2}")

if __name__ == "__main__":
    report_path = '/Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester2/cl1_14apr26/final_report.md'
    pdf_path = '/Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester2/cl1_14apr26/final_report.pdf'
    
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report_text = f.read()
        save_markdown_to_pdf(report_text, pdf_path, title="HMM & CRF Sequence Modeling Report")
    else:
        print(f"Report file not found: {report_path}")
