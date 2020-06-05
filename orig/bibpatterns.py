import re

try:
    from bibnouns import (
        LANGUAGENAMES,
        OCEANNAMES,
        COUNTRIES,
        CONTINENTNAMES,
        CITIES,
        OCCURREDREPLACEMENTS,
    )
except ImportError:
    from langsci.bibnouns import (
        LANGUAGENAMES,
        OCEANNAMES,
        COUNTRIES,
        CONTINENTNAMES,
        CITIES,
        OCCURREDREPLACEMENTS,
    )


PRESERVATIONPATTERN = re.compile(
    r"\b(%s)\b"
    % (
        "|".join(
            LANGUAGENAMES
            + COUNTRIES
            + OCEANNAMES
            + CONTINENTNAMES
            + CITIES
            + OCCURREDREPLACEMENTS
        )
    )
)
CONFERENCEPATTERN = re.compile(
    "([A-Z][^ ]*[A-Z][A-Z-a-z]]+)"
)  # Binnenmajuskeln should be kept
PROCEEDINGSPATTERN = re.compile(
    "(.* (?:Proceedings|Workshop|Conference|Symposium).*)\}$"
)  # Binnenmajuskeln should be kept
VOLUMEPATTERN = re.compile("(, )?([Vv]olume|[Vv]ol.?|Band|[Tt]ome) *([0-9IVXivx]+)")
THESISPATTERN = re.compile("(.*?)( doctoral)? dissertation")


# pattern definitions
year = "\(? *(?P<year>[12][678901][0-9][0-9][a-f]?) *\)?"
pages = u"(?P<pages>[0-9xivXIV]+[-––]+[0-9xivXIV]+)"
pppages = u"\(?[Pps\. ]*%s\)?" % pages
author = "(?P<author>.*?)"  # do not slurp the year
ed = "(?P<ed>\([Ee]ds?\.?\))?"
editor = "(?P<editor>.+)"
booktitle = "(?P<booktitle>.+)"
title = "(?P<title>.*?)"
journal = "(?P<journal>.*?)"
note = "(?P<note>.*)"
numbervolume = "(?P<volume>[-\.0-9/]+) *(\((?P<number>[-0-9/]+)\))?"
pubaddr = "(?P<address>.+) *:(?!/) *(?P<publisher>[^:]\.?[^\.]+)"
#                      for http://                For J. Smith
seriesnumber = "(?P<newtitle>.*) \((?P<series>.*?) +(?P<number>[-\.0-9/]+)\)"
url = r"(?P<url>(https?://)?www\.[a-zA-Z0-9-]+\.[-A-Za-z0-9\.]+(/[^ ]+)?)\.?"
NUMBERVOLUME = re.compile(numbervolume)
SERIESNUMBER = re.compile(seriesnumber)
URL = re.compile(url)
urlyear = "[12][0-9][0-9][0-9]"
urlmonth = "[10]?[0-9]"
urlday = "[0123]?[0-9]"
URLDATE = re.compile(
    "[\[\(]?({urlyear}-{urlmonth}-{urlday}|{urlday}.{urlmonth}.{urlyear}|{urlday}/{urlmonth}/{urlyear}|{urlmonth}/{urlday}/{urlyear})[\]\)]?".format(
        urlyear=urlyear, urlday=urlday, urlmonth=urlmonth
    )
)

# compiled regexes
BOOK = re.compile(
    u"{author}[., ]* {ed}[\., ]*{year}[\., ]*{title}\. +{pubaddr}\. *{note}".format(
        author=author, ed=ed, year=year, title=title, pubaddr=pubaddr, note=note
    )
)
ARTICLE = re.compile(
    u"{author}[., ]*{year}[., ]*{title}\. +{journal}[\.,]? *{numbervolume}[\.,:] *{pages}{note}".format(
        pages=pppages,
        author=author,
        year=year,
        journal=journal,
        numbervolume=numbervolume,
        title=title,
        note=note,
    )
)
ONLINEARTICLE = re.compile(
    u"{author}[., ]*{year}[., ]*{title}\. +{journal}[\.,]? *{numbervolume}[\.,:] *{url}.{note}".format(
        pages=pppages,
        author=author,
        year=year,
        journal=journal,
        numbervolume=numbervolume,
        url=url,
        title=title,
        note=note,
    )
)
INCOLLECTION = re.compile(
    u"{author}[., ]*{year}[., ]*{title}\. In {editor} \([Ee]ds?\. *\)[\.,]? {booktitle}[\.,] {pages}\. +{pubaddr}\.{note}".format(
        author=author,
        year=year,
        title=title,
        editor=editor,
        booktitle=booktitle,
        pages=pppages,
        pubaddr=pubaddr,
        note=note,
    )
)
MISC = re.compile(
    "{author}[., ]*{year}[., ]*{title}\. *(?P<note>.*)".format(
        author=author, year=year, title=title
    )
)

# regexes for telling entry types
EDITOR = re.compile(
    "[0-9]{4}.*(\([Ee]ds?\.?\))"
)  # make sure the editor of @incollection is only matched after the year
PAGES = re.compile(pages)
PUBADDR = re.compile(pubaddr)


TYPKEYFIELDS = r"^([^\{]+)\{([^,]+),[\s\n\t]*((?:.|\n)*)\}"
