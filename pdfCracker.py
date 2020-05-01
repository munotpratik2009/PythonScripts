from PyPDF2 import PdfFileWriter, PdfFileReader

def decryptPdf(f):
        for ps in range(3000000, 9999999):
		print('Current Run:' + str(ps))
		if(f.getIsEncrypted()):
			t = f.decrypt(str(ps) + '7257')
			if (t==1 or t==2):
				print(str(ps) + '7257')
				return {'pdf': f, 'r': ran, 's': str(ps) + '7257'}

f = PdfFileReader(open("XXXXXXXXX.pdf", "rb"))
o = f.decrypt('PRAT0712')
print(o)
print(f.getDocumentInfo())
print (f.getDocumentInfo().title)
