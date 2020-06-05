"""Conform BibTeX files and repair common errors

Attributes:
  keys: a dictionary of all BibTeX keys of the type "Smith2001", used for checking for duplicates 
  excludefields: fields which not be output in the normalized file
"""

import sys
import re
import pprint
import glob
import string
import argparse

try:
    from asciify import (
        ASCIITRANS,
        FRENCH_REPLACEMENTS,
        GERMAN_REPLACEMENTS,
        ICELANDIC_REPLACEMENTS,
        asciify,
    )
    from bibnouns import (
        LANGUAGENAMES,
        OCEANNAMES,
        COUNTRIES,
        CONTINENTNAMES,
        CITIES,
        OCCURREDREPLACEMENTS,
    )
    from delatex import dediacriticize
    from bibtools import *
except ImportError:
    from langsci.asciify import (
        ASCIITRANS,
        FRENCH_REPLACEMENTS,
        GERMAN_REPLACEMENTS,
        ICELANDIC_REPLACEMENTS,
        asciify,
    )
    from langsci.bibnouns import (
        LANGUAGENAMES,
        OCEANNAMES,
        COUNTRIES,
        CONTINENTNAMES,
        CITIES,
        OCCURREDREPLACEMENTS,
    )
    from langsci.delatex import dediacriticize
    from langsci.bibtools import *

"""
usage: python3 normalizebib.py localbibliography.bib [--restrict]

The modified records are in sorted.bib
"""
parser = argparse.ArgumentParser(
    description="Normalize input bib file and write output to sorted.bib"
)
parser.add_argument("bibfilename", type=str, help="The bib file to be processed")
parser.add_argument(
    "--restrict",
    action="store_true",
    help="Restrict the output to keys found in the tex files",
)
args = parser.parse_args()

texdir = "chapters"
outfilename = "sorted.bib"

texfiles = glob.glob("%s/*tex" % texdir)
CITE = re.compile(r"\\cite[yeargenltp]*(?:\[.*?\])?\{(.*?)\}")
#                                         pages     key
# accumulate the keys of cited works per tex-file
citations = []
for texfile in texfiles:
    citations += [
        c.strip()
        for cs in CITE.findall(open(texfile).read())
        for c in cs.split(",")  # there might be multiple keys per cite command
    ]
citations = list(set(citations))  # uniq
# store in dict for more efficient checking for presence
citationsd = dict(zip(citations, [True for t in range(len(citations))]))
# access bib file
bibfile = open(args.bibfilename).read()
newbib = normalize(bibfile, inkeysd=citationsd, restrict=args.restrict)
# write out
outbib = open(outfilename, "w")
outbib.write(newbib)
outbib.close()
