import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from db.DataModel import Lecture, db
from pdfminer.pdftypes import PDFException
import peewee
import os.path


class Pdf2Txt(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.caching = True
        self.codec = 'utf-8'
        self.laparams = LAParams()
        self.imagewriter = None
        self.pagenos = set()
        self.maxpages = 0
        self.password = ''
        self.rotation = 0

    def __convert(self, ifile, ofile=None):
        fp = file(ifile, 'rb')

        if ofile is None:
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
        if ofile is None:
            retval = outfp.getvalue()

        outfp.close()
        return retval

    def extract_text(self):
        lectures = Lecture.select().where(Lecture.content == '', Lecture.url % "*pdf")

        for lecture in list(lectures):
            if not os.path.exists(self.prefix+lecture.path):
                print "File not found: {0}".format(lecture.path)
                continue
            print lecture.url
            lecture.content = self.__convert(self.prefix+lecture.path)
            try:
                with db.transaction():
                    lecture.save()
            except peewee.OperationalError as e:
                print e