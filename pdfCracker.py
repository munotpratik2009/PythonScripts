"""
A basic attempt to PDF cracking. 
I had a pdf which was password protected and I had lost the password. 
I partially remembered the password and I wanted to write a program 
which will generate the password based on this partial password. 
And it did work! I was able to open the file with this password
generator
"""

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
