from pypdf import PdfReader, PdfWriter

def remove_all_text_layer(input_pdf_path, output_pdf_path):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        # This method attempts to remove all text operations
        writer.add_page(page).remove_text()

    with open(output_pdf_path, "wb") as output_pdf_file:
        writer.write(output_pdf_file)
    
    print(f"All text removed and saved to {output_pdf_path}")

# --- Usage Example ---
input_file = 'templates/contrato-medico-04.pdf'
output_file = 'contratos/Contrato_sem_texto.pdf'


# Make sure 'original.pdf' exists in the same directory
remove_all_text_layer(input_file, output_file)
