import fitz

doc = fitz.open("/Users/sampath/Desktop/1BF24AI146_SakethRamArepalli_IST-Report.pdf")
page = doc[0]

text_dict = page.get_text("dict")
for block in text_dict.get("blocks", []):
    if "lines" in block:
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if text:
                    print(f"Text: '{text}' | BBox: {span['bbox']} | Font: {span['font']} | Size: {span['size']}")
doc.close()
