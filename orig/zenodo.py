"""
A bridge between the LangSci LaTeX skeleton and the Zenodo API

"""

import requests
import json
import pprint
import re
import sys

try:
    from texpatterns import *
except ImportError:
    from langsci.texpatterns import *


class Publication:
    """
  A Publication holds all the metadata which are 
  generic for books and papers
  """

    def __init__(self):
        self.metadata = {
            "upload_type": "publication",
            "access_right": "open",
            "license": "cc-by",
            "imprint_publisher": "Language Science Press",
            "imprint_place": "Berlin",
            "communities": [{"identifier": "langscipress"}],
            "prereserve_doi": True,
            "language": "eng",
        }

    def register(self, token):
        """
    register the publication with Zenodo
    """

        data = {"metadata": self.metadata}
        pprint.pprint(json.dumps(data))

        r = requests.post(
            "https://zenodo.org/api/deposit/depositions",
            params={"access_token": token},
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
        )
        pprint.pprint(r.json())
        try:
            return r.json()["metadata"]["prereserve_doi"]["doi"]
        except KeyError:
            print(r.json()["errors"])
            raise


class Book(Publication):
    """ 
  A full-length publication, either a monograph or an edited volume 
  """

    def __init__(self):
        Publication.__init__(self)
        self.title = None
        self.authors = []
        self.abstract = "Abstract could not be found"
        self.keywords = []
        self.digitalisbn = None
        self.getBookMetadata()
        self.chapter = []
        self.getChapters()
        self.metadata["publication_type"] = "book"
        # self.metadata['related_identifiers'] = [{'isAlternateIdentifier':self.digitalisbn}]    #currently not working on Zenodo
        self.metadata["title"] = self.title
        self.metadata["description"] = self.abstract
        self.metadata["creators"] = [{"name": au} for au in self.authors]
        self.metadata["keywords"] = self.keywords

    def getBookMetadata(self):
        """
    Parse the file localmetadata.tex and retrieve the metadata
    """

        localmetadataf = open("localmetadata.tex", encoding="utf-8")
        localmetadata = localmetadataf.read()
        localmetadataf.close()
        self.title = TITLEP.search(localmetadata).group(1)
        print(self.title)
        authorstring = BOOKAUTHORP.search(localmetadata).group(1)
        authors = []
        for i, au in enumerate(LASTAND.split(authorstring)):
            if (
                i % 2 == 0
            ):  # get rid of splitters, i.e. "and" and "lastand" at odd positions
                authors.append(au.strip())
        self.authors = authors
        self.abstract = BACKBODYP.search(localmetadata).group(1)
        try:
            self.keywords = [
                x.strip()
                for x in KEYWORDSEPARATOR.split(
                    CHAPTERKEYWORDSP.search(localmetadata).group(1)
                )
            ]
        except:
            pass
        self.digitalisbn = ISBNP.search(localmetadata).group(1)

    def getChapters(self):
        """
    find all chapters in edited volumes which are referenced in main.tex 
    """

        mainf = open("main.tex", encoding="utf-8")
        main = mainf.read()
        mainf.close()
        chapterpaths = INCLUDEPAPERP.findall(main)
        self.chapters = [
            Chapter(cp, booktitle=self.title, isbn=self.digitalisbn)
            for cp in chapterpaths
        ]


class Chapter(Publication):
    """
  A chapter in an edited volume
  """

    def __init__(self, path, booktitle="", isbn=False):
        print("reading", path)
        Publication.__init__(self)
        chapterf = open("chapters/%s.tex" % path, encoding="utf-8")
        chapter = chapterf.read()
        chapterf.close()
        preamble = chapter.split("\\begin{document}")[0]
        abstract = ABSTRACTP.search(preamble).group(1)
        if "noabstract" in abstract:
            abstract = "replace this dummy abstract in Zenodo"
        keywords = []
        try:
            keywords = [
                x.strip() for x in CHAPTERKEYWORDSP.search(preamble).group(1).split(",")
            ]
        except:
            pass
        self.path = path.strip()
        self.abstract = abstract
        self.keywords = keywords
        self.pagerange = ""
        for l in open("collection_tmp.bib", encoding="utf-8").readlines():
            if l.startswith("@incollection{chapters/%s," % path):
                # print(path)
                self.pagerange = PAGERANGEP.search(l).group(1)
                self.authors = [
                    au.strip() for au in BIBAUTHORP.search(l).group(1).split(" and ")
                ]
                self.title = BIBTITLEP.search(l).group(1)
                break  # we have found the entry we are interested in
        self.title = self.title.replace("{", "").replace("}", "")
        self.booktitle = booktitle
        if isbn:
            self.bookisbn = isbn
        self.metadata["publication_type"] = "section"
        self.metadata["imprint_isbn"] = self.bookisbn
        self.metadata["partof_title"] = self.booktitle
        self.metadata["title"] = self.title
        self.metadata["description"] = self.abstract
        try:
            self.metadata["partof_pages"] = self.pagerange.replace("--", "-")
        except TypeError:
            self.metadata["partof_pages"] = self.pagerange
        # retrieve affiliations from texfile
        authoraffiliations = CHAPTERAUTHORP.findall(preamble)
        orcidgroups = ORCIDSP.findall(preamble)
        # store the affiliations in a dictionary
        creatorsdic = {}
        for authoraffiliation in authoraffiliations:
            # ["and", "John Smith", "Harvard"]. Ignore first element
            creatorsdic[authoraffiliation[1].strip()] = authoraffiliation[2].replace(
                "\&", "&"
            )
        print(creatorsdic)
        orcidsdic = {}
        for orcidgroup in orcidgroups:
            # ["and", "John Smith", "123456"]. Ignore first element
            orcidauthorname = (
                orcidgroup[1].split("\\")[0].strip()
            )  # split on \ to get rid of \affiliation...
            orcidsdic[orcidauthorname] = orcidgroup[2].strip()
            # add affiliations where available in dictionary
            self.metadata["creators"] = [
                {
                    "name": au,
                    "affiliation": creatorsdic.get(au, " "),
                    "orcid": orcidsdic.get(au, " "),
                }
                for au in self.authors
            ]
        self.metadata["keywords"] = self.keywords
        # self.metadata['related_identifiers'] = [{'hasPart':self.bookisbn}] #unintuitive directionality of hasPart and isPart
