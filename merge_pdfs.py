import fitz

def merge_pdfs():
    # Final output filename
    output_filename = "IST_AAT_Report_Sampath_1BF24AI147.pdf"

    # Create a new empty PDF
    result_doc = fitz.open()

    # Open cover and body
    cover = fitz.open("cover.pdf")
    body = fitz.open("body_report.pdf")

    # Insert cover (1st page)
    result_doc.insert_pdf(cover)

    # Insert the rest of the report (all pages)
    result_doc.insert_pdf(body)

    # Save
    result_doc.save(output_filename)
    
    cover.close()
    body.close()
    result_doc.close()
    print(f"Successfully generated {output_filename}")

if __name__ == '__main__':
    merge_pdfs()
