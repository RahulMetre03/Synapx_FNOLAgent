from PyPDF2 import PdfReader

def readpdf(path):
    reader = PdfReader(path)

    text = ""
    number = 1
    for page in reader.pages:
        if number < 3:
            text += page.extract_text()
            number = number + 1
    # print(repr(text))
    return repr(text)
