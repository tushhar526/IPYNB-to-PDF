import nbformat
from nbconvert.exporters import WebPDFExporter
from traitlets.config import Config
import os
import uuid
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

def convert_ipynb_to_pdf(ipynb_path, output_pdf_path):
    with open(ipynb_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    c = Config()
    c.WebPDFExporter.allow_chromium_download = True
    c.WebPDFExporter.template_name = 'classic'
    c.WebPDFExporter.exclude_input_prompt = True
    c.WebPDFExporter.exclude_output_prompt = True
    c.WebPDFExporter.extra_css = """
    @page {
      margin: 0.5cm !important;
    }
    .jp-Notebook {
      padding: 0 !important;
      margin: 0 !important;
    }
    .jp-Cell {
      margin-bottom: 0.2em !important;
      margin-top: 0.2em !important;
    }
    """

    pdf_exporter = WebPDFExporter(config=c)
    print(f"Converting {ipynb_path} to PDF using WebPDFExporter...")
    (body, resources) = pdf_exporter.from_notebook_node(notebook)

    with open(output_pdf_path, 'wb') as pdf_file:
        pdf_file.write(body)

    print(f"Exported PDF: {output_pdf_path}")
    return output_pdf_path

def merge_pdfs(pdf_file_paths, output_merged_pdf):
    """
    Merges a list of PDF files into a single PDF.
    """
    print(f"Merging {len(pdf_file_paths)} PDFs into {output_merged_pdf}")
    writer = PdfWriter()

    for pdf_path in pdf_file_paths:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_merged_pdf, 'wb') as merged_pdf:
        writer.write(merged_pdf)

    print(f"Merged PDF saved as: {output_merged_pdf}")
    return output_merged_pdf

def add_page_number(input_pdf_path, output_pdf_with_numbers_path):
    """
    Adds page numbers to every page of the input PDF.
    """
    print(f"Adding page numbers to: {input_pdf_path}")

    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    total_pages = len(reader.pages)

    for page_num in range(total_pages):
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        # Simple page number at the bottom center
        page_label = f"{page_num + 1}"
        can.setFont("Helvetica", 9)
        can.drawCentredString(300, 15, page_label)
        can.save()

        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        watermark_page = watermark_pdf.pages[0]

        page = reader.pages[page_num]
        page.merge_page(watermark_page)
        writer.add_page(page)

    with open(output_pdf_with_numbers_path, 'wb') as output_pdf:
        writer.write(output_pdf)

    print(f"Saved PDF with page numbers: {output_pdf_with_numbers_path}")

def process_ipynb_files(ipynb_file_paths, upload_dir='upload', output_dir='output'):
    """
    Main function for Flask: Converts, merges, and adds page numbers to PDFs from ipynb files.
    Returns the final numbered PDF path.
    """
    processed_pdfs = []
    for ipynb_path in ipynb_file_paths:
        base_name = os.path.splitext(os.path.basename(ipynb_path))[0]
        temp_pdf = os.path.join(output_dir, f"{base_name}_{uuid.uuid4().hex[:6]}_raw.pdf")
        convert_ipynb_to_pdf(ipynb_path, temp_pdf)
        processed_pdfs.append(temp_pdf)

    merge_pdf_path = os.path.join(output_dir, f"Merged_{uuid.uuid4().hex[:6]}.pdf")
    merge_pdfs(processed_pdfs, merge_pdf_path)

    # Clean up individual raw PDFs
    for temp_pdf in processed_pdfs:
        try:
            os.remove(temp_pdf)
        except Exception as e:
            print(f"Could not remove temp PDF {temp_pdf}: {e}")

    # Add page numbers to the merged PDF
    final_pdf_with_numbers = os.path.join(output_dir, f"Merged_{uuid.uuid4().hex[:6]}.pdf")
    add_page_number(merge_pdf_path, final_pdf_with_numbers)
    try:
        os.remove(merge_pdf_path)
    except Exception as e:
        print(f"Could not remove merged PDF {merge_pdf_path}: {e}")

    print("Final PDF saved at:", final_pdf_with_numbers)
    print("Generated PDF size:", os.path.getsize(final_pdf_with_numbers))

    return final_pdf_with_numbers
