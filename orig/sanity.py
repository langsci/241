"""
Check files of various types for conformity to Language Science Press guidelines. Currently the following 
file types are checked: 

* tex files from folder chapters/
* bib files 
* png/jpg files in forlder figures/

Attributes:
  SPELLD: A US-English dictionary 
  TKNZR: A US_English tokenizer
  LATEXTERMS: LaTeX terms which the spell checker should treat as conformant
"""

import re
import glob
import sys
import fnmatch
import os
import textwrap
import uuid

# import enchant
# from enchant.tokenize import get_tokenizer
from PIL import Image


# SPELLD = enchant.Dict("en_US")
# TKNZR = get_tokenizer("en_US")
# LATEXTERMS = ("newpage","clearpage","textit","textbf","textsc","textwidth","tabref","figref","sectref","emph")


class SanityError:
    """A record of a potentially problematic passage
  
  Attributes:
    filename (str): the path to the file where the error is found
    linenr (int): the number of the line where the error is found 
    line (str): the full line under consideration
    offendingstring (str): the string which was identified as problematic
    msg (str): information on why this string was found problematic
    pre (str): left context of the offending string
    post (str): right context of the offending string
    ID (str): ID to uniquely refer to a given error in HTML-DOM
    name (str): hexadecimal string used for colour coding based on msg
    color (str): a rgb color string
    bordercolor (str): a rgb color string, which is darker than color 
  """

    def __init__(self, filename, linenr, line, offendingstring, msg):
        self.filename = filename.split("/")[-1]
        self.linenr = linenr
        self.line = line
        self.offendingstring = offendingstring
        self.msg = msg
        self.pre = self.line.split(self.offendingstring)[0]
        try:
            self.post = self.line.split(self.offendingstring)[1]
        except IndexError:
            self.post = ""
        self.ID = uuid.uuid1()
        self.name = str(hash(msg))[-6:]
        # compute rgb colors from msg
        t = textwrap.wrap(self.name, 2)[-3:]
        self.color = "rgb({},{},{})".format(
            int(t[0]) + 140, int(t[1]) + 140, int(t[2]) + 140
        )
        self.bordercolor = "rgb({},{},{})".format(
            int(t[0]) + 100, int(t[1]) + 100, int(t[2]) + 100
        )

    def __str__(self):
        return "{linenr}: …{offendingstring}… \t{msg}".format(**self.__dict__)


class SanityFile:
    """A file with information about potentially problematic passages
  
  Attributes:
    filename (str): the path to the file
    content (str): the content of the file 
    lines ([]str): the lines of the file 
    errors ([]SanityError): the list of found errors
    spellerrors ([]SanityError): the list of words not found in the spell dictionary
  
  """

    def __init__(self, filename):
        self.filename = filename
        self.errors = []
        try:
            self.content = open(filename, encoding="utf-8").read()
        except UnicodeDecodeError:
            print("file %s is not in proper Unicode encoding" % filename)
            self.content = ""
            self.errors = [
                SanityError(
                    filename, 0, " ", " ", "file not in Unicode, no analysis possible"
                )
            ]
        self.lines = self.split_(self.content)
        # self.spellerrors = []

    def split_(self, c):
        result = self._removecomments(c).split("\n")
        return result

    def _removecomments(self, s):
        """strip comments from file so that errors are not marked in comments"""

        # negative lookbehind
        try:
            result = re.sub("(?<!\\\\)%.*\n", "\n", s)
        except TypeError:
            print("%s could not be regexed" % s)
            return s
        return result

    def check(self):
        """ 
    check the file for errors
    """

        for i, line in enumerate(self.lines):
            if "\\chk" in line:  # the line is explicitely marked as being correct
                continue
            for antipattern, msg in self.antipatterns:
                m = re.search("(%s)" % antipattern, line)
                if m != None:
                    g = m.group(1)
                    if g != "":
                        self.errors.append(SanityError(self.filename, i, line, g, msg))
            for positivepattern, negativepattern, msg in self.posnegpatterns:
                posmatch = re.search("(%s)" % positivepattern, line)
                if posmatch == None:
                    continue
                # a potentiall incorrect behaviour is found, but could be saved by the presence of additional material
                g = posmatch.group(1)
                negmatch = re.search(negativepattern, line)
                if (
                    negmatch == None
                ):  # the match required to make this line correct is not found
                    self.errors.append(SanityError(self.filename, i, line, g, msg))

    def spellcheck(self):
        """return a list of all words which are neither known LaTeX terms nor found in the enchant dictionary
    """
        result = sorted(
            list(
                set(
                    [
                        t[0]
                        for t in TKNZR(self.content)
                        if SPELLD.check(t[0]) == False and t[0] not in LATEXTERMS
                    ]
                )
            )
        )
        self.spellerrors = result


class TexFile(SanityFile):
    """
  A tex file to be checked 
  
  Attributes:
    antipatterns (str[]): a list of 2-tuples consisting of a string to match and a message to deliver if the string is found 
    posnegpatterns (str[]): a list of 3-tuples consisting a pattern to match, a pattern NOT to match, and a message 
    filechecks: currently unused #TODO
  """

    antipatterns = (
        (
            r" et al.",
            "Please use the citation commands \\citet and \\citep",
        ),  # et al in main tex
        (r"setfont", "You should not set fonts explicitely"),  # no font definitions
        (
            r"\\(small|scriptsize|footnotesize)",
            "Please consider whether changing font sizes manually is really a good idea here",
        ),  # no font definitions
        (
            r"([Tt]able|[Ff]igure|[Ss]ection|[Pp]art|[Cc]hapter\() *\\ref",
            "It is often advisable to use the more specialized commands \\tabref, \\figref, \\sectref, and \\REF for examples",
        ),  # no \ref
        # ("",""),      #\ea\label
        # ("",""),      #\section\label
        (" \\footnote", "Footnotes should not be preceded by a space"),
        # ("",""),      #footnotes end with .
        (
            r"\[[0-9]+,[0-9]+\]",
            "Please use a space after the comma in lists of numbers ",
        ),  # no 12,34 without spacing
        (
            r"\([^)]+\\cite[pt][^)]+\)",
            "In order to avoid double parentheses, it can be a good idea to use \\citealt instead of \\citet or \\citep",
        ),
        ("([0-9]+-[0-9]+)", "Please use -- for ranges instead of -"),
        # (r"[0-9]+ *ff","Do not use ff. Give full page ranges"),
        (r"[^-]---[^-]", "Use -- with spaces rather than ---"),
        (r"tabular.*\|", "Vertical lines in tables should be avoided"),
        (r"\\hline", "Use \\midrule rather than \\hline in tables"),
        (
            r"\\gl[lt] *[a-z].*[\.?!] *\\\\ *$",
            "Complete sentences should be capitalized in examples",
        ),
        (r"\\glt * ``", "Use single quotes for translations."),
        (r"\\section.*[A-Z].*[A-Z].*", "Only capitalize this if it is a proper noun"),
        (
            r"\\s[ubs]+ection.*[A-Z].*[A-Z].*",
            "Only capitalize this if it is a proper noun",
        ),
        (
            r"[ (][12][8901][0-9][0-9]",
            "Please check whether this should be part of a bibliographic reference",
        ),
        (
            r"(?<!\\)[A-Z]{3,}",
            "It is often a good idea to use \\textsc\{smallcaps} instead of ALLCAPS",
        ),
        (
            r"(?<![0-9])[?!;\.,][A-Z]",
            "Please use a space after punctuation (or use smallcaps in abbreviations)",
        ),  # negative lookbehind for numbers because of lists of citation keys
        (
            r"\\textsuperscript\{w\}",
            "Please use Unicode ʷ for labialization instead of superscript w",
        ),
        (
            r"\\textsuperscript\{j\}",
            "Please use Unicode ʲ for palatalization instead of superscript j",
        ),
        (
            r"\\textsuperscript\{h\}",
            "Please use Unicode ʰ for aspiration instead of superscript h",
        ),
    )

    posnegpatterns = (
        (
            r"\[sub]*section\{",
            r"\label",
            "All sections should have a \\label. This is not necessary for subexamples.",
        ),
        # (r"\\ea.*",r"\label","All examples should have a \\label"),
        (
            r"\\gll\W+[A-Z]",
            r"[\.?!][ }]*\\\\ *$",
            "All vernacular sentences should end with punctuation",
        ),
        (
            r"\\glt\W+[A-Z]",
            r"[\.?!][}\\]*['’”ʼ]",
            "All translated sentences should end with punctuation",
        ),
    )

    filechecks = (
        # ("",""),    #src matches #imt
        # ("",""),     #words
        # ("",""),     #hyphens
        # ("",""),    #tabulars have lsptoprule
        # ("",""),    #US/UK
    )


# year not in order in multicite


class BibFile(SanityFile):
    """ 
  A bib file to be checked 
  
  Attributes:
    antipatterns (str[]): a list of 2-tuples consisting of a string to match and a message to deliver if the string is found 
  """

    antipatterns = (
        # ("[Aa]ddress *=.*[,/].*[^ ]","No more than one place of publication. No indications of countries or provinces"), #double cities in address
        # ("[Aa]ddress *=.* and .*","No more than one place of publication."), #double cities in address
        (
            "[Tt]itle * =.*: +(?<!{)[a-zA-Z]+",
            "Subtitles should be capitalized. In order to protect the capital letter, enclose it in braces {} ",
        ),
        (
            "[Aa]uthor *=.*(?<=(and|AND|..[,{])) *[A-Z]\..*",
            "Full author names should be given. Only use abbreviated names if the author is known to prefer this. It is OK to use middle initials",
        ),
        (
            "[Ee]ditor *=.*(?<=(and|AND|..[,{])) *[A-Z]\..*",
            "Full editor names should be given. Only use abbreviated names if the editor is known to prefer this. It is OK to use middle initials",
        ),
        (
            "[Aa]uthor *=.* et al",
            "Do not use et al. in the bib file. Give a full list of authors",
        ),
        ("[Aa]uthor *=.*&.*", "Use 'and' rather than & in the bib file"),
        (
            "[Tt]itle *=(.* )?[IVXLCDM]*[IVX]+[IVXLCDM]*[\.,\) ]",
            "In order to keep the Roman numbers in capitals, enclose them in braces {}",
        ),
        ("\.[A-Z]", "Please use a space after a period or an abbreviated name"),
    )

    posnegpatterns = []


class ImgFile(SanityFile):
    """ 
    An image file to be checked 
    """

    def __init__(self, filename):
        self.filename = filename
        self.errors = []
        self.spellerrors = []
        self.latexterms = []

    def check(self):
        try:
            img = Image.open(self.filename)
        except IOError:
            print("could not open", self.filename)
            return
        try:
            x, y = img.info["dpi"]
            if x < 72 or y < 72:
                print("low res for", self.filename.split)
                self.errors.append(
                    SanityError(
                        self.filename,
                        "",
                        "",
                        "low resolution",
                        "%sx%sdpi, required 300" % (x, y),
                    )
                )
        except KeyError:
            x, y = img.size
            if x < 1500:
                estimatedresolution = x / 5
                print(
                    "resolution of %s when printed full with: %i. Required: 300"
                    % (self.filename.split("/")[-1], estimatedresolution)
                )
                self.errors.append(
                    SanityError(
                        self.filename,
                        "low resolution",
                        " ",
                        " ",
                        "estimated %sdpi, required 300" % estimatedresolution,
                    )
                )


class SanityDir:
    """
  A directory with various files to be checked
  """

    def __init__(self, dirname, ignorecodes):
        self.dirname = dirname
        self.ignorecodes = ignorecodes
        self.texfiles = self.findallfiles("tex")
        self.bibfiles = self.findallfiles("bib")
        self.pngfiles = self.findallfiles("png")
        self.jpgfiles = self.findallfiles("jpg")
        self.texterrors = {}
        self.imgerrors = {}

    def findallfiles(self, extension):
        """
    find all files in or below the current directory with a given extension 
    
    args:
      extension (str):  the extension to be looked for 
      
    returns: 
      a list of paths for the retrieved files
    """

        matches = []
        localfiles = glob.glob("%s/local*" % self.dirname)
        chapterfiles = glob.glob("%s/chapters/*tex" % self.dirname)
        imgfiles = glob.glob("%s/figures/*" % self.dirname)
        for filename in fnmatch.filter(
            localfiles + chapterfiles + imgfiles, "*.%s" % extension
        ):
            matches.append(os.path.join(self.dirname, filename))
        return sorted(matches)

    def printErrors(self):
        """
    Print all identified possible erros with metadata (filename, line number, reason
        """
        for filename in sorted(self.texterrors):
            fileerrors = self.texterrors[filename]
            print(
                "\n",
                70 * "=",
                "\n%s, %i possible errors found." % (filename, len(fileerrors)),
                "Suppressing %i error codes: %s"
                % (len(self.ignorecodes), ",".join(self.ignorecodes)),
                "\n",
                70 * "=",
            )
            # print(fileerrors)
            for e in fileerrors:
                if e.name not in self.ignorecodes:
                    print("    ", e.name, e)
        for filename in self.imgerrors:
            fileerrors = self.imgerrors[filename]
            for e in fileerrors:
                print(filename)
                print("    ", e)

    def check(self):
        """
    Check all files in the directory
    """

        for tfilename in self.texfiles:
            try:
                t = TexFile(tfilename)
            except AttributeError:
                print(tfilename)
                continue
            t.check()
            # t.spellcheck()
            self.texterrors[tfilename] = t.errors
            # self.errors[tfilename][1] = t.spellerrors
        for bfilename in self.bibfiles:
            b = BibFile(bfilename)
            b.check()
            self.texterrors[bfilename] = b.errors
            # self.errors[bfilename][1] = b.spellerrors
        for ifilename in self.pngfiles + self.jpgfiles:
            imgf = ImgFile(ifilename)
            imgf.check()
            # self.spellerrors = []
            self.imgerrors[ifilename] = imgf.errors
