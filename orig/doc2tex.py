import sys
import os
import codecs

try:
    from convertertools import convert
except ImportError:
    from langsci.convertertools import convert

filename = sys.argv[1]
currentworkingdirectory = os.getcwd()
doc = convert(filename, tmpdir=currentworkingdirectory, wd=currentworkingdirectory)

out1 = codecs.open("temporig.tex", "w", "utf-8")
out1.write(doc.text)
out1.close()

out2 = codecs.open("temp.tex", "w", "utf-8")
#print(repr(doc.modtext[353900:353980]))
out2.write(doc.modtext)
out2.close()

out3 = codecs.open("chapter.tex", "w", "utf-8")
out3.write(doc.papertext)
out3.close()
