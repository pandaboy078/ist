import fitz

doc = fitz.open("/Users/sampath/Desktop/1BF24AI146_SakethRamArepalli_IST-Report.pdf")
page = doc[0]

# Blank out Title and SDG area
page.draw_rect(fitz.Rect(165, 242, 550, 285), color=(1,1,1), fill=(1,1,1))

# Blank out Name
page.draw_rect(fitz.Rect(305, 305, 550, 325), color=(1,1,1), fill=(1,1,1))

# Blank out USN
page.draw_rect(fitz.Rect(320, 335, 550, 355), color=(1,1,1), fill=(1,1,1))

# Insert Title Label
page.insert_text((170, 256), "Title:", fontname="Times-Bold", fontsize=12)
# Insert Title Text
page.insert_text((205, 256), "IPL Batsman Efficiency Analysis Using Statistical Sampling Techniques", fontname="Times-Roman", fontsize=11)
# Insert Subtitle
page.insert_text((205, 268), "Green Dot Ball Sustainability Initiative", fontname="Times-Roman", fontsize=11)

# Insert SDG Addressed
page.insert_text((170, 280), "SDG Addressed:", fontname="Times-Bold", fontsize=11)
page.insert_text((260, 280), "SDG 13 – Climate Action, SDG 15 – Life on Land", fontname="Times-Roman", fontsize=11)

# Insert New Name
page.insert_text((308, 318), "Sampath Kumar", fontname="Times-Roman", fontsize=12)

# Insert New USN
page.insert_text((326, 348), "1BF24AI147", fontname="Times-Roman", fontsize=12)

# Save only the first page
doc_new = fitz.open()
doc_new.insert_pdf(doc, from_page=0, to_page=0)
doc_new.save("cover.pdf")
doc_new.close()
doc.close()
