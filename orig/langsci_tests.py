import unittest

import indextools
import asciify
import bibtools
import delatex

class TestFixIndex(unittest.TestCase):
    """ Test the adaption of the indexes
    """

    def test_fixindex(self):
        """ Test a full index line
        """
        result = indextools.processline(r"\indexentry {\v{C}{\'{e}}pl\"o, Slavomír@\v{C}{\'{e}}pl\"o, Slavomír|hyperpage}{2}")
        self.assertEqual(result, r"\indexentry {Ceplo, Slavomir@\v{C}{\'{e}}pl\"o, Slavomír|hyperpage}{2}")
        
        
        
class TestASCII(unittest.TestCase):
    """ Test the adaption of the indexes
    """
        
        
    def test_asciify(self):
        """ Test an isolated string
        """
        result = asciify.asciify("Nædéßoþ")
        self.assertEqual(result, "Naedessoth")
        
    def test_dediacriticize(self):
        """ Test an isolated string
        """
        result = delatex.dediacriticize(r"Bád\'ag\'{a}p{\'{a}}")
        self.assertEqual(result, "Bádagapa")
        
        
        result = delatex.dediacriticize(r"Bád\'ag\'{a}p{\'{a}}", stripbraces=False)
        self.assertEqual(result, "Bádagap{a}")
        
        result = delatex.dediacriticize(r"""\'{a}\`{a}\^{a}\~{a}\"{a}\={a}\.{a}\d{a}\v{a}\H{a}\u{a}\k{a}""")
        self.assertEqual(result, "aaaaaaaaaaaa")
        
class TestBibConversion(unittest.TestCase):
    """ Test the conversion of inline literature references to BibTex
    """
    maxDiff=None
    
    def test_record(self):
        bibtests = (
                    ("""Mufwene, Salikoko. 2001. The Ecology of Language Evolution. Cambridge: Cambridge University Press.""",
                        """@book{Mufwene2001,\n\taddress = {Cambridge},\n\tauthor = {Mufwene, Salikoko},\n\tpublisher = {Cambridge University Press},\n\ttitle = {The Ecology of Language Evolution},\n\tyear = {2001}\n}\n"""),
                    ("""Alleyne, Mervyn C. 1996. Syntaxe historique créole. Paris, France: Karthala."""
                                ,"""@book{Alleyne1996,\n\taddress = {Paris, France},\n\tauthor = {Alleyne, Mervyn C.},\n\tpublisher = {Karthala},\n\ttitle = {Syntaxe historique créole},\n\tyear = {1996}\n}\n"""),
                    ("""Allsopp, Richard. (ed.), 2003. Dictionary of Caribbean English usage. Kingston, Jamaica: University of the West Indies Press."""
                                ,"""@book{Allsopp2003,\n\taddress = {Kingston, Jamaica},\n\tbooktitle = {Dictionary of {Caribbean} {English} usage},\n\teditor = {Allsopp, Richard},\n\tpublisher = {University of the West Indies Press},\n\ttitle = {Dictionary of {Caribbean} {English} usage},\n\tyear = {2003}\n}\n"""),
                    ("""Ammon, Matthias. 2013. The functions of oath and pledge in Anglo-Saxon legal culture. Historical Research. 86(233), 515-535."""
                                ,"""@article{Ammon2013,\n\tauthor = {Ammon, Matthias},\n\tjournal = {Historical Research},\n\tnumber = {233},\n\tpages = {515--535},\n\ttitle = {The functions of oath and pledge in {Anglo}-{Saxon} legal culture},\n\tvolume = {86},\n\tyear = {2013}\n}\n"""),
                    ("""Andriotis, Nikolaos. 1995. History of the Greek Language: Four studies. Thessaloniki, Greece: Ίδρυμα Τριανταφυλλίδη."""
                                ,"""@book{Andriotis1995,\n\taddress = {Thessaloniki, Greece},\n\tauthor = {Andriotis, Nikolaos},\n\tpublisher = {Ίδρυμα Τριανταφυλλίδη},\n\ttitle = {History of the {Greek} Language: {{F}}our studies},\n\tyear = {1995}\n}\n"""),
                    ("""Archer, Dawn. 2010. Speech acts. In Andreas H. Jucker & Irma Taavitsainen (eds.), Historical pragmatics, 379-418. Berlin, Germany: Walter de Gruyter GmbH & Co."""
                                ,"""@incollection{Archer2010,\n\taddress = {Berlin, Germany},\n\tauthor = {Archer, Dawn},\n\tbooktitle = {Historical pragmatics},\n\teditor = {Andreas H. Jucker and Irma Taavitsainen},\n\tpages = {379--418},\n\tpublisher = {Walter de Gruyter GmbH & Co},\n\ttitle = {Speech acts},\n\tyear = {2010}\n}\n"""),
                    ("""Auer, Peter & Hinskens, Frans & Kerswill, Paul. (eds.), 2005.  Dialect change: Convergence and divergence in European languages. Cambridge, England: The Cambridge University Press. """
                                ,"""@book{AuerEtAl2005,\n\taddress = {Cambridge, England},\n\tbooktitle = {Dialect change: {{C}}onvergence and divergence in {European} languages},\n\teditor = {Auer, Peter and Hinskens, Frans and Kerswill, Paul},\n\tpublisher = {The Cambridge University Press},\n\ttitle = {Dialect change: {{C}}onvergence and divergence in {European} languages},\n\tyear = {2005}\n}\n"""),
                    ("""Awbery, G. M. 1988. Slander and defamation as a source for historical dialectology. In Alan R. Thomas (ed.), Methods in dialectology: Proceedings of the sixth international conference held at the University College of North Wales, 3rd-7th August 1987, 164-174. Clevedon, PA: Multilingual Matters Ltd."""
                                ,"""@incollection{Awbery1988,\n\taddress = {Clevedon, PA},\n\tauthor = {Awbery, G. M.},\n\tbooktitle = {Methods in dialectology: {{P}}roceedings of the sixth international conference held at the University College of {North} {Wales}, 3rd-7th {August} 1987},\n\teditor = {Alan R. Thomas},\n\tpages = {164--174},\n\tpublisher = {Multilingual Matters Ltd},\n\ttitle = {Slander and defamation as a source for historical dialectology},\n\tyear = {1988}\n}\n"""),
                    ("""Bailey, Guy & Ross, Garry. 1988. The shape of the superstrate: Morphosyntactic features of Ship English. English World-Wide. 9(2). 193-212."""
                                ,"""@article{BaileyRoss1988,\n\tauthor = {Bailey, Guy and Ross, Garry},\n\tjournal = {English World-Wide},\n\tnumber = {2},\n\tpages = {193--212},\n\ttitle = {The shape of the superstrate: {{M}}orphosyntactic features of Ship {English}},\n\tvolume = {9},\n\tyear = {1988}\n}\n"""),
                    ("""Baker, Philip & Huber, Magnus. 2001. Atlantic, Pacific, and world-wide features in English-lexicon contact languages. English World-Wide. 22(2), 157-208."""
                                ,"""@article{BakerHuber2001,\n\tauthor = {Baker, Philip and Huber, Magnus},\n\tjournal = {English World-Wide},\n\tnumber = {2},\n\tpages = {157--208},\n\ttitle = {{Atlantic}, {Pacific}, and world-wide features in {English}-lexicon contact languages},\n\tvolume = {22},\n\tyear = {2001}\n}\n"""),
                    ##(""""""  ,""""""),
                    ("""Blevins, Juliette. 2004. Evolutionary phonology. Cambridge: Cambridge University Press."""
                                ,"""@book{Blevins2004,\n\taddress = {Cambridge},\n\tauthor = {Blevins, Juliette},\n\tpublisher = {Cambridge University Press},\n\ttitle = {Evolutionary phonology},\n\tyear = {2004}\n}\n"""),
                    ("""Casali, Roderic F. 1998. Predicting ATR activity. Chicago Linguistic Society (CLS) 34(1). 55-68."""
                                ,"""@article{Casali1998,\n\tauthor = {Casali, Roderic F.},\n\tjournal = {Chicago Linguistic Society (CLS)},\n\tnumber = {1},\n\tpages = {55--68},\n\ttitle = {Predicting {ATR} activity},\n\tvolume = {34},\n\tyear = {1998}\n}\n"""),
                    ("""Chomsky, Noam. 1986. Knowledge of language. New York: Praeger."""
                                ,"""@book{Chomsky1986,\n\taddress = {New York},\n\tauthor = {Chomsky, Noam},\n\tpublisher = {Praeger},\n\ttitle = {Knowledge of language},\n\tyear = {1986}\n}\n"""),
                    ("""van Coetsem, Frans. 2000. A general and unified theory of the transmission process in language contact. Heidelberg: Winter."""
                                ,"""@book{vanCoetsem2000,\n\taddress = {Heidelberg},\n\tauthor = {van Coetsem, Frans},\n\tpublisher = {Winter},\n\ttitle = {A general and unified theory of the transmission process in language contact},\n\tyear = {2000}\n}\n"""),
                    ("""Franks, Steven. 2005. Bulgarian clitics are positioned in the syntax. http://www.cogs.indiana.edu/people/homepages/franks/Bg_clitics_remark_dense.pdf (17 May, 2006.)"""
                                ,"""@misc{Franks2005,\n\tauthor = {Franks, Steven},\n\tnote = {(17 May, 2006.)},\n\ttitle = {{Bulgarian} clitics are positioned in the syntax},\n\turl = {http://www.cogs.indiana.edu/people/homepages/franks/Bg_clitics_remark_dense.pdf},\n\tyear = {2005}\n}\n"""),
                    ("""Iverson, Gregory K. 1983. Korean /s/. Journal of Phonetics 11. 191-200."""
                                ,"""@article{Iverson1983,\n\tauthor = {Iverson, Gregory K.},\n\tjournal = {Journal of Phonetics},\n\tpages = {191--200},\n\ttitle = {{Korean} /s/},\n\tvolume = {11},\n\tyear = {1983}\n}\n"""),
                    ("""Iverson, Gregory K. 1989. On the category supralaryngeal. Phonology 6. 285-303."""
                                ,"""@article{Iverson1989,\n\tauthor = {Iverson, Gregory K.},\n\tjournal = {Phonology},\n\tpages = {285--303},\n\ttitle = {On the category supralaryngeal},\n\tvolume = {6},\n\tyear = {1989}\n}\n"""),
                    ("""Johnson, Kyle, Mark Baker & Ian Roberts. 1989. Passive arguments raised. Linguistic Inquiry 20. 219-251."""
                                ,"""@article{JohnsonRoberts1989,\n\tauthor = {Johnson, Kyle, Mark Baker and Ian Roberts},\n\tjournal = {Linguistic Inquiry},\n\tpages = {219--251},\n\ttitle = {Passive arguments raised},\n\tvolume = {20},\n\tyear = {1989}\n}\n"""),
                    ("""Lahiri, Aditi (ed.). 2000. Analogy, leveling, markedness: Principles of change in phonology and morphology (Trends in Linguistics 127). Berlin: Mouton de Gruyter."""
                                ,"""@book{Lahiri2000,\n\taddress = {Berlin},\n\tbooktitle = {Analogy, leveling, markedness: {{P}}rinciples of change in phonology and morphology},\n\teditor = {Lahiri, Aditi},\n\tnumber = {127},\n\tpublisher = {Mouton de Gruyter},\n\tseries = {Trends in Linguistics},\n\ttitle = {Analogy, leveling, markedness: {{P}}rinciples of change in phonology and morphology},\n\tyear = {2000}\n}\n"""),
                    ("""McCarthy, John J. & Alan S. Prince. 1999. Prosodic morphology. In John A. Goldsmith (ed.), Phonological theory: The essential readings, 238-288. Malden, MA & Oxford: Blackwell."""
                                ,"""@incollection{McCarthyPrince1999,\n\taddress = {Malden, MA \& Oxford},\n\tauthor = {McCarthy, John J. and Alan S. Prince},\n\tbooktitle = {Phonological theory: {{T}}he essential readings},\n\teditor = {John A. Goldsmith},\n\tpages = {238--288},\n\tpublisher = {Blackwell},\n\ttitle = {Prosodic morphology},\n\tyear = {1999}\n}\n"""),
                    ("""Murray, Robert W. & Theo Vennemann. 1983. Sound change and syllable structure in Germanic phonology. Language 59(3). 514-528."""
                                ,"""@article{MurrayVennemann1983,\n\tauthor = {Murray, Robert W. and Theo Vennemann},\n\tjournal = {Language},\n\tnumber = {3},\n\tpages = {514--528},\n\ttitle = {Sound change and syllable structure in {Germanic} phonology},\n\tvolume = {59},\n\tyear = {1983}\n}\n"""),
                    #("""Oxford English Dictionary , 2nd edn. 1989. Oxford: Oxford University Press."""
                                #,""""""),
                    ("""Pedersen, Johan. 2005. The Spanish impersonal se-construction: Constructional variation and change. Constructions 1. http://www.constructions-online.de. (3 April, 2007.)"""
                                ,"""@article{Pedersen2005,\n\tauthor = {Pedersen, Johan},\n\tjournal = {Constructions},\n\tnote = {(3 April, 2007.)},\n\ttitle = {The {Spanish} impersonal se-construction: {{C}}onstructional variation and change},\n\turl = {http://www.constructions-online.de},\n\tvolume = {1},\n\tyear = {2005}\n}\n"""),
                    ("""Rissanen, Matti. 1999. Syntax. In Roger Lass (ed.), Cambridge History of the English Language, vol. 3, 187-331. Cambridge & New York: Cambridge University Press."""
                                ,"""@incollection{Rissanen1999,\n\taddress = {Cambridge \& New York},\n\tauthor = {Rissanen, Matti},\n\tbooktitle = {{Cambridge} History of the {English} Language},\n\teditor = {Roger Lass},\n\tpages = {187--331},\n\tpublisher = {Cambridge University Press},\n\ttitle = {Syntax},\n\tvolume = {3},\n\tyear = {1999}\n}\n"""),
                    ("""Stewart, Thomas W., Jr. 2000. Mutation as morphology: Bases, stems, and shapes in Scottish Gaelic. Columbus, OH: The Ohio State University dissertation."""
                                ,"""@thesis{Stewart2000,\n\taddress = {Columbus, OH},\n\tauthor = {Stewart, Thomas W., Jr},\n\tschool = {The Ohio State University},\n\ttitle = {Mutation as morphology: {{B}}ases, stems, and shapes in {Scottish} {Gaelic}},\n\tyear = {2000}\n}\n"""),
                    ("""Webelhuth, Gert (ed.). 1995. Government and binding theory and the minimalist program: Principles and parameters in syntactic theory. Oxford: Blackwell."""
                                ,"""@book{Webelhuth1995,\n\taddress = {Oxford},\n\tbooktitle = {Government and binding theory and the minimalist program: {{P}}rinciples and parameters in syntactic theory},\n\teditor = {Webelhuth, Gert},\n\tpublisher = {Blackwell},\n\ttitle = {Government and binding theory and the minimalist program: {{P}}rinciples and parameters in syntactic theory},\n\tyear = {1995}\n}\n"""),
                    ("""Yu, Alan C. L. 2003. The morphology and phonology of infixation. Berkeley, CA: University of California dissertation."""
                                ,"""@thesis{Yu2003,\n\taddress = {Berkeley, CA},\n\tauthor = {Yu, Alan C. L.},\n\tschool = {University of California},\n\ttitle = {The morphology and phonology of infixation},\n\tyear = {2003}\n}\n"""),
                    #("""Smith, John. 2000. Thoughts on stuff. Newton: Mypress. www.mypress.com/smith""",
                                #"""@book{Smith2000,\n\taddress = {Newton},\n\tauthor = {Smith, John},\n\tpublisher = {Mypress},\n\ttitle = {Thoughts on stuff},\n\turl = {www.mypress.com/smith},\n\tyear = {2000}\n}\n"""),
                    ("""Smith, John. 2000. Thoughts on stuff. Newton: Mypress. www.mypress.com/smith (2021-12-24)""",
                        """@book{Smith2000,\n\taddress = {Newton},\n\tauthor = {Smith, John},\n\tpublisher = {Mypress},\n\ttitle = {Thoughts on stuff},\n\turl = {www.mypress.com/smith},\n\turldate = {2021-12-24},\n\tyear = {2000}\n}\n"""),
                    #("""Smith, John. 2000. Thoughts on stuff. Newton: Mypress. www.mypress.com/smith (2021-12-24) and so on"""      ,""""""),
                    ("""Braun, Sabine & Sara Dicerto. 2016. The use of videoconferencing in proceedings conducted with the assistance of an interpreter. http://www.videoconference-interpreting.net/wp-content/uploads/2016/11/AVIDICUS3_Research_Report.pdf"""
                        ,"""@misc{BraunDicerto2016,\n\tauthor = {Braun, Sabine and Sara Dicerto},\n\ttitle = {The use of videoconferencing in proceedings conducted with the assistance of an interpreter},\n\turl = {http://www.videoconference-interpreting.net/wp-content/uploads/2016/11/AVIDICUS3_Research_Report.pdf},\n\tyear = {2016}\n}\n"""),
                    #("""bad Url"""      ,""""""),
                    #("""masters thesis"""     ,""""""),
                    #("Parkvall, Mikael. 2005. Foreword. In Alan D. Corré (ed.), A glossary of lingua franca. https://minds.wisconsin.edu/bitstream/item/3920/edition2/edition3/foreword.htm (Accessed 2016-10-07).",""""""),
                    #("maitrise",""""""),
                    #("maitrise",""""""),
                    #("maitrise","""""")
                    #Maynor, Natalie. 1988. Written records of spoken language: How reliable are they? In Alan R. Thomas (ed.), Methods in dialectology: Proceedings of the sixth international conference held at the University College of North Wales, 3rd-7th August 1987, 109-120. Clevedon, PA: Multilingual Matters Ltd.
                    )
        for s, expected in bibtests:
            record = bibtools.Record(s)
            self.assertEqual(record.bibstring, expected)
      
      #TODO add more and different entry types of varying complexity
    
        
if __name__ == '__main__':
    unittest.main()