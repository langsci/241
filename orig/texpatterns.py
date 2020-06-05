"""
A couple of regexes to retrieve metadata from tex files used at Language Science Press

Atttributes:
    INCLUDEPAPERP: a regex for finding all \include'd papers in a fiel
    BOOKAUTHORP: a regex for finding the authors of books in a tex file
    LASTAND: a regex to find "\lastand" or "\and", used by LaTeX to join author names
    CHAPTERAUTHORP: a regex to find authors and affiliations of chapter authors
    TITLEP: a regex to find a title 
    ISBNP: a regex to retrieve the digital ISBN 
    CHAPTERKEYWORDSP: a regex to retrieve the keywords
    ABSTRACTP: a regex to retrieve the abstract 
    BACKBODYP: a regex to retrieve the blurb 
    KEYWORDSEPARATOR:  a regex for symbols people use to separate keywords 
    PAGERANGEP: a regex for retrieving page ranges 
    BIBAUTHORP: a regex to retrieve the author field from a BibTeX file
    BIBTITLEP: a regex to retrieve the author field from a BibTeX file
"""

import re

INCLUDEPAPERP = re.compile(
    r"\n[\t ]*\\includepaper\{chapters/(.*?)\}"
)  # only papers on new lines, ignoring % comments
BOOKAUTHORP = re.compile(r"\\author{(.*?)}")
LASTAND = re.compile(r"(\\lastand|\\and)")
CHAPTERAUTHORP = re.compile(r"\\(author{|and|lastand)(.*?) *\\affiliation{(.*?)}")
ORCIDSP = re.compile(r"\\(author{|and|lastand)(.*?) *\\orcid{(.*?)}")
TITLEP = re.compile(r"\\title{(.*?)}")
ISBNP = re.compile(r"\\lsISBNdigital}{(.*)}")
CHAPTERKEYWORDSP = re.compile(r"\\keywords{(.*?)}")
ABSTRACTP = re.compile(r"\\abstract{(.*?)[}\n]")
BACKBODYP = re.compile(r"\\BackBody{(.*?)[}\n]")
KEYWORDSEPARATOR = re.compile("[,;-]")

BIBAUTHORP = re.compile(r"author={([^}]+)")  # current setup adds space after author
BIBTITLEP = re.compile(r"title={{([^}]+)}}")
PAGERANGEP = re.compile("{([0-9ivx]+--[0-9ivx]+)}")
