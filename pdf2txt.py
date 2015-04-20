import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from tutorial.DataModel import Lecture, db
from pdfminer.pdftypes import PDFException
import peewee
import os.path

class Pdf2Txt(object):
    def __init__(self):
        self.caching = True
        self.codec = 'utf-8'
        self.laparams = LAParams()
        self.imagewriter = None
        self.pagenos = set()
        self.maxpages = 0
        self.password = ''
        self.rotation = 0

    def convert(self, ifile, ofile=None):
        fp = file(ifile, 'rb')

        if ofile == None:
            outfp = StringIO.StringIO()
        else:
            outfp = file(ofile, 'wb')

        rsrcmgr = PDFResourceManager(caching=self.caching)
        device = TextConverter(rsrcmgr, outfp, codec=self.codec, laparams=self.laparams,
                               imagewriter=self.imagewriter)

        interpreter = PDFPageInterpreter(rsrcmgr, device)
        try:
            for page in PDFPage.get_pages(fp, self.pagenos,
                                          maxpages=self.maxpages, password=self.password,
                                          caching=self.caching, check_extractable=True):
                page.rotate = (page.rotate + self.rotation) % 360
                interpreter.process_page(page)
        except PDFException as e:
            print "Could not extract text {0}".format(e)
        fp.close()
        device.close()
        retval = None
        if ofile == None:
            retval = outfp.getvalue()

        outfp.close()
        return retval

def main():
    pdf2txt = Pdf2Txt()
    lectures = Lecture.select().where(Lecture.content == '').limit(1000)
    for lecture in lectures:
        if not os.path.exists(lecture.path):
            print "File not found: {0}".format(lecture.path)
            continue
        print lecture.url
        lecture.content = pdf2txt.convert(lecture.path)
        try:
            with db.transaction():
                lecture.save()
        except peewee.OperationalError as e:
            print e

    # ifile = '/Users/martin/Dropbox/kool/business_intelligence_seminar/project/tutorial/pdf/2015/cg/spring/Main/Lectures/Geometry.pdf'
    # ofile = '/Users/martin/Dropbox/kool/business_intelligence_seminar/project/tutorial/pdf/2015/cg/spring/Main/Lectures/ttt.txt'
    # print "start convert ..."
    # content = pdf2txt.convert(ifile)
    # print "{0}".format(content[0:100])
    # print "... done"

if __name__ == '__main__':
    main()
