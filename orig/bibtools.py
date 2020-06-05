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
    from asciify import ASCIITRANS, FRENCH_REPLACEMENTS, GERMAN_REPLACEMENTS, ICELANDIC_REPLACEMENTS, asciify
    from bibnouns import LANGUAGENAMES, OCEANNAMES, COUNTRIES, CONTINENTNAMES, CITIES, OCCURREDREPLACEMENTS
    from delatex import dediacriticize
    import bibpatterns
except ImportError:
    from langsci.asciify import ASCIITRANS, FRENCH_REPLACEMENTS, GERMAN_REPLACEMENTS, ICELANDIC_REPLACEMENTS, asciify
    from langsci.bibnouns import LANGUAGENAMES, OCEANNAMES, COUNTRIES, CONTINENTNAMES, CITIES, OCCURREDREPLACEMENTS
    from langsci.delatex import dediacriticize
    from langsci import bibpatterns

keys = {} #store for all bibtex keys

#The following fields will not be included in the normalizedfile
excludefields = ['abstract',
                 'language',
                 'date-added',
                 'date-modified',
                 'rating',
                 'keywords',
                 'issn',
                 'timestamp',
                 'owner',
                 'optannote',
                 'optkey',
                 'optmonth',
                 'optnumber',
                 'url_checked',
                 'optaddress',
                 'eprinttype',
                 'bdsk-file-1',
                 'bdsk-file-2',
                 'bdsk-file-3',
                 'bdsk-url-1',
                 'bdsk-url-2',
                 'bdsk-url-3'] #fields not to output



#fields to output
FIELDS = ["key",
    "title",
    "booktitle",
    "author",
    "editor",
    "year",
    "journal",
    "volume",
    "number",
    "pages",
    "address",
    "publisher",
    "note",
    "url",
    "series"
    ]


class Record():
  """
  A bibtex record

  Attributes:
    TYPEKEYFIELDS (str): a regex for finding all the BibTeX keys of the type "Smith2001"

  """


  def __init__(self,s,fromfile=False,inkeysd={},restrict=False,reporting=[]):
    """
    :param s: the bibtexrecord as a string
    :type s: string or unicode
    :param inkeys: keys which should be included in the output
    :type inkeys: list of strings
    :param restrict: whether the output bibfile should be restricted to inkeys
    :type restrict: Boolean
    """
    self.errors = [] #accumulates all error messages
    self.reporting = []

    if fromfile: #get record from a file
        m = re.match(bibpatterns.TYPKEYFIELDS,s)
        try:
            self.typ = m.group(1).lower()
        except AttributeError:
            return
        self.key = m.group(2)

        #analyze remainder
        try:
            self.fields = dict((tp[0].strip().lower()\
                .replace('\n',' ')\
                .replace('\t',' '),
                tp[1].strip()\
                .replace('\n',' ')\
                .replace('\t',' ')
                    ) for tp in [re.split('\s*=\s*',t,maxsplit=1)
                for t in re.split('(?<=\})\s*,\s*\n',
                    m.group(3).strip()
                    )
                ]
                    )
        except IndexError:
            print(s)
        #store keys
        self.inkeysd = inkeysd
        self.restrict = restrict
        self.reporting = reporting
        if self.key in keys:
            self.errors.append("duplicate key %s"% self.key)
            keys[self.key] = True
    else: #get record from a one-line string
        s=s.strip()
        self.orig = s
        self.bibstring = s
        d = {} # a dictionary to hold the retrieved fields
        self.typ = "misc"
        self.key = None
        d["title"] = None
        d["booktitle"] = None
        d["author"] = "Anonymous"
        d["editor"] = None
        d["year"] = None
        d["journal"] = None
        d["volume"] = None
        d["number"]  = None
        d["pages"] = None
        d["address"] = None
        d["publisher"] = None
        d["note"] = None
        d["url"] = None
        if  bibpatterns.EDITOR.search(s):
            self.typ = "incollection"
            m = bibpatterns.INCOLLECTION.search(s)
            if m:
                d["author"] = m.group('author')
                d["editor"] = m.group('editor')
                d["title"] = m.group('title')
                d["booktitle"] = m.group('booktitle')
                d["year"] = m.group('year')
                d["address"] = m.group('address')
                d["publisher"] = m.group('publisher')
                d["pages"] = m.group('pages')
                d["note"] = m.group('note')
        elif  bibpatterns.ARTICLE.search(s):
            self.typ = "article"
            m = bibpatterns.ARTICLE.search(s)
            if m:
                d["author"] = m.group('author')
                d["title"] = m.group('title')
                d["year"] = m.group('year')
                d["journal"] = m.group('journal')
                d["number"] = m.group('number')
                d["volume"] = m.group('volume')
                d["pages"] = m.group('pages')
                d["note"] = m.group('note')
        elif  bibpatterns.NUMBERVOLUME.search(s) and bibpatterns.URL.search(s) and bibpatterns.ONLINEARTICLE.search(s):
            self.typ = "article"
            m = bibpatterns.ONLINEARTICLE.search(s)
            if m:
                d["author"] = m.group('author')
                d["title"] = m.group('title')
                d["year"] = m.group('year')
                d["journal"] = m.group('journal')
                d["number"] = m.group('number')
                d["volume"] = m.group('volume')
                d["url"] = m.group('url')
                d["note"] = m.group('note')
        elif bibpatterns.PUBADDR.search(s):
            self.typ = "book"
            m = bibpatterns.BOOK.match(s)
            if m:
                d["author"] = m.group('author')
                if m.group('ed') != None:
                    d["editor"] = m.group('author')
                    d["author"] = None
                d["title"] = m.group('title')
                d["year"] = m.group('year')
                d["address"] = m.group('address')
                d["publisher"] = m.group('publisher')
                d["note"] = m.group('note')
        else:
            m = bibpatterns.MISC.search(s)
            if m:
                d["author"] = m.group('author')
                d["title"] = m.group('title')
                d["year"] = m.group('year')
                d["note"] = m.group('note')
        if d["note"] == '.':
            d["note"] = None
        try:
            d["author"] = d["author"].replace(' &', ' and ').replace('\ ', ' ')
        except AttributeError:
            try:
                d["editor"] = d["editor"].replace(' &', ' and ')
            except AttributeError:
                return
        if d["note"] and re.search(bibpatterns.URL,d["note"]):
            url = re.search(bibpatterns.URL,d["note"]).group()
            if url != None:
                d["note"] = d["note"].replace(url,'').strip()
                d["url"] = url
        if d["title"]:
            m = bibpatterns.SERIESNUMBER.match(d["title"])
            if m:
                d["series"] = m.group('series')
                d["number"] = m.group('number')
                d["title"] = m.group('newtitle')
        #http
        #series volume
        creator = ''
        creatorpart = "Anonymous"
        yearpart = "9999"
        try:
            creatorpart = d["author"].split(',')[0].replace(' ', '')
            creator = d["author"]
        except AttributeError:
            creatorpart = d["editor"].split(',')[0].split(' ')[0]
            creator = d["editor"]
        try:
            yearpart = d["year"][:4]
        except TypeError:
            return
        andcount = creator.count(' and ')
        ampcount = creator.count('&')
        authorcount = 1 + andcount + ampcount
        print(creator,andcount,ampcount)
        if authorcount > 2:
            creatorpart += "EtAl"
        if authorcount == 2:
            secondcreator = re.split(" and ",creator)[-1].strip()
            if ',' in secondcreator:
                creatorpart += secondcreator.split(',')[0]
            elif ' ' in secondcreator:
                creatorpart += secondcreator.split(' ')[-1]
            else:
                creatorpart += secondcreator
        self.key = creatorpart+yearpart
        self.fields = d
    self.conform()
    self.report()
    self.bibstring="@%s{%s,\n\t"%(self.typ,self.key)
    self.bibstring+=",\n\t".join(sorted(["%s = {%s}"%(f,self.fields[f]) for f in self.fields if self.fields[f] not in ('',None)]))
    self.bibstring+="\n}\n"

  def conform(self):
    """
    analyze fields, report errors and correct as necessary
    """

    if self.fields.get('editor') != None and self.fields.get('booktitle') == None:
      try:
        self.fields['booktitle'] = self.fields['title']
      except KeyError:
        self.errors.append("neither title nor booktitle")
    pages = self.fields.get('pages')
    if pages != None:
      self.fields['pages'] = re.sub(r'([0-9])-([0-9])',r'\1--\2',pages)
    self.conformtitles()
    self.checkvolumenumber()
    self.conforminitials()
    self.correctampersand()
    self.checketal()
    self.checkand()
    self.checkedition()
    self.checkurldate()
    self.checkurl()
    self.checkquestionmarks()
    self.checkarticle()
    self.checkthesis()
    self.checkbook()
    self.checkincollection()
    self.checklanguagenames()

  def report(self):
    """
    print errors, if any
    """
    try:
        if len(self.errors)>0:
            restrict =  True
            if restrict==False or self.inkeysd.get(self.key):
                print(self.key,'\n  '.join(['  ']+self.errors))
    except AttributeError:
        pass


  def upperme(self,match):
    """
    substitute a regex match with uppercase
    """

    return match.group(1) + ' {{' +match.group(2).upper()+'}}'

  def checklanguagenames(self):
    #CONFERENCEPATTERN = re.compile("([A-Z][^ ]*[A-Z][A-Z-a-z]]+)") #Binnenmajuskeln should be kept
    #PROCEEDINGSPATTERN = re.compile("(.* (?:Proceedings|Workshop|Conference|Symposium).*)\}$") #Binnenmajuskeln should be kept

    ts = ['title','booktitle']
    for t in ts:
      try:
        oldt = self.fields.get(t,' ')
        preservationt = str(oldt)
        for match in bibpatterns.PRESERVATIONPATTERN.finditer(preservationt):
            group = match.group(1)
            preservationt = preservationt.replace(group,"{%s}"%group)
            if oldt != preservationt:
              if 'nouns' in self.reporting:
                print(oldt,' ==> ',preservationt)
              self.fields[t] = preservationt
      except AttributeError:
        pass
      try:
        oldt = self.fields.get(t,'')
        conft = str(oldt)
        m = bibpatterns.CONFERENCEPATTERN.search(conft)
        if m:
          for g in m.groups():
            conft = conft.replace(g,"{%s}"%g)
            if oldt != conft:
              if 'conferences' in self.reporting:
                print(oldt,' ==> ',conft)
              self.fields[t] = conft
      except AttributeError:
        pass


      try:
        oldt = self.fields.get(t,'')
        proct = str(oldt)
        m = bibpatterns.PROCEEDINGSPATTERN.search(proct)
        if m:
          for g in m.groups():
            proct = proct.replace(g,"{%s}"%g)
            if oldt != proct:
              if 'conferences' in self.reporting:
                print(oldt,' ==> ',proct)
              self.fields[t] = proct
      except AttributeError:
        pass





  def conformtitles(self):
    """
    uppercase and protect first word of subtitle
    protect capitals inside a word
    protect lone capitals
    """

    for t in ('title','booktitle'):
      if self.fields.get(t) != None:
        self.fields[t] = re.sub(r'([:\.\?!]) *([a-zA-Z])', self.upperme ,self.fields[t])
        self.fields[t] = re.sub(r'([A-Z][a-z]*[A-Z]+)', r"{\1}" ,self.fields[t])
        self.fields[t] = re.sub(r' ([A-Z]) ', r" {{\1}} " ,self.fields[t])

  def checkvolumenumber(self):
    if self.typ == "book":
        m = bibpatterns.VOLUMEPATTERN.search(self.fields["title"])
        if m != None:
            vol = m.group(3)
            print(vol)
            self.fields["volume"] = vol
            self.fields["title"] = self.fields["title"].replace(m.group(),'')
    if self.typ == "incollection":
        try:
          m = bibpatterns.VOLUMEPATTERN.search(self.fields["booktitle"])
        except KeyError:
          self.fields["booktitle"]="{\\biberror{no booktitle}}"
          self.errors.append("no booktitle")
          return
        if m != None:
            vol = m.group(3)
            self.fields["volume"] = vol
            self.fields["booktitle"] = self.fields["booktitle"].replace(m.group(),'')

  def conforminitials(self):
    """
    make sure that initials have a space between them and that initials have a period
    """

    for t in ('author','editor'):
      if self.fields.get(t) != None:
        self.fields[t] = re.sub(r'([A-Z])\.([A-Z])', r'\1. \2',self.fields[t])
        #print(1,self.fields[t])
        self.fields[t] = re.sub(' ([A-Z]$)', r' \1.',self.fields[t])
        #print(2,self.fields[t])


  def correctampersand(self):
    """
    Replace & by " and " as required by BibTeX
    """

    for t in ('author','editor'):
      if self.fields.get(t) != None:
        self.fields[t] = self.fields[t].replace(r" & ", " and ")
        self.fields[t] = self.fields[t].replace(r" \& ", " and ")
        self.fields[t] = self.fields[t].replace("  ", " ")

    for t in ['address']:
      if self.fields.get(t) != None:
        self.fields[t] = self.fields[t].replace(r" & ", " \& ")

  def checkand(self):
    """
    check whether commas are used instead of 'and' (asyndetic coordination)
    """

    for t in ('author','editor'):
      if self.fields.get(t) != None:
        ands = self.fields[t].count(' and ')
        commas = self.fields[t].count(',')
        if commas > ands +1:
          self.errors.append("problem with commas in %s: %s"% (t,self.fields[t]))

  def checketal(self):
    """
    check whether literal 'et al' is used in author or editor fields
    """

    for t in ('author','editor'):
      if self.fields.get(t) != None:
          if "et al" in self.fields[t]:
            self.fields[t] = self.fields[t].replace("et al","\\biberror{et al}")
            self.errors.append("literal et al in  %s: %s"% (t,self.fields[t]))

  def checkedition(self):
    """
    check for the correct formatting of the edition field
    """

    edn =  self.fields.get('edition')
    if edn:
      edn = edn.replace('{','').replace('}','').replace('"','').strip()
      try:
        int(edn)
      except ValueError:
          self.errors.append("incorrect format for edition: %s"% (edn))

  def checkurl(self):
    """
    make sure the url field contains the url and only the url
    """
    url = self.fields.get('url',False)
    if url:
        if url.endswith('.'):
            url = url[:-1]
            self.fields['url'] = url

        if url != None and url.count(' ')>0:
            self.errors.append("space in url")
        nonsites = ('ebrary','degruyter','doi','myilibrary','academia','ebscohost')
        for n in nonsites:
            if url != None and  n in url:
                self.errors.append("%s: urls should only be given for true repositories or for material not available elsewhere"%url)

  def checkurldate(self):
    """
    make sure the urldate field is only present when an url is actually given
    """

    datefound = False
    if not self.fields.get('urldate'):
        url = self.fields.get('url',False)
        if url:
            substrings =  url.split(' ')
            if len(substrings) == 2:
                newurl, urldate = substrings
                if re.search('[12][0-9][0-9][0-9]', urldate):
                    for c in "[]()":#remove parentheses
                        urldate = urldate.replace(c,'')
                    self.fields['url'] = newurl
                    self.fields['urldate'] = urldate
        if datefound:
            return
        else:
            note = self.fields.get('note',False)
        if note:
            m = bibpatterns.URLDATE.search(note)
            if m != None:
                urldate = m.group(1)
                for c in "[]()":#remove parentheses
                    urldate = urldate.replace(c,'')
                self.fields['urldate'] = urldate
                self.fields['note'] = self.fields['note'].replace(m.group(0),'')

    else:
        if self.fields.get('url') == None:
            self.errors.append("urldate without url")

  def checkthesis(self):
    if self.typ != 'book':
      return
    m = bibpatterns.THESISPATTERN.search(self.fields.get("publisher",""))
    if m != None:
        self.typ = "thesis"
        school = m.group(1)
        self.fields["school"] = school
        thesistype = m.group(2)
        if m.group(2) in ("doctoral","PhD"):
            self.typ = "phdthesis"
        del self.fields["publisher"]


  def checkbook(self):
    """
    perform some check for type book
    """

    if self.typ != 'book':
      return
    self.placelookup()
    mandatory = ('year', 'title', 'address', 'publisher')
    for m in mandatory:
      self.handleerror(m)
    if self.fields.get('series') != None:
      #people often mix up the field 'number' and 'volume' for series
      #if both are present, we leave everything as is
      #if only volume is present, we assign the content to
      #number and delete the field volume
      number = self.fields.get('number')
      volume = self.fields.get('volume')
      if volume != None:
        if number == None:
          self.fields['number'] = volume
          del self.fields['volume']
    #books should have either author or editor, but not both or none
    auth = self.fields.get('author')
    ed = self.fields.get('editor')
    if auth:
      if ed:
        self.errors.append("both author and editor")
      else:
        self.addsortname(auth)
    elif ed:
      self.addsortname(ed)
    else:
      self.errors.append("neither author nor editor")

  def addsortname(self,name):
    """
    add an additional field for sorting for names with diacritics
    """

    try:
        residue = name.translate({ord(i):None for i in string.ascii_letters+'- ,{}.'})
    except  TypeError: #python2
        residue = ''
    if residue == '':
      pass
    else:
      self.fields['sortname']= asciify(dediacriticize(name))

  def checkarticle(self):
    """
    perform some checks for type article
    """
    if self.typ != 'article':
      return
    mandatory = ('author', 'year', 'title', 'journal', 'volume')

    if self.fields.get('volume') == None and self.fields.get('number') != None:
      self.fields['volume'] = self.fields['number']
      del self.fields['number']
    for m in mandatory:
      self.handleerror(m)
    if self.fields.get('pages') == None: #only check for pages if no electronic journal
      if self.fields.get('url') == None:
            self.fields['pages'] = r"{\biberror{no pages}}"
            self.errors.append("missing pages")
    auth = self.fields.get('author')
    if auth:
      self.addsortname(auth)

  def placelookup(self):
    """
    Provide addresses for some well-known publishers if addresses are missing
    """
    if not self.fields.get('address'):
      publisher = self.fields.get('publisher','')
      if "John Benjamins" in publisher:
        self.fields['address'] = "{Amsterdam}"
      elif "Cambridge" in publisher or "CUP" in publisher :
        self.fields['address'] = "{Cambridge}"
      elif "Oxford" in publisher or "OUP" in publisher :
        self.fields['address'] = "{Oxford}"
      elif "Blackwell" in publisher or "Routledge" in publisher :
        self.fields['address'] = "{London}"
      elif "Gruyter" in publisher or "Mouton" in publisher :
        self.fields['address'] = "{Berlin}"
      elif "Wiley" in publisher:
        self.fields['address'] = "{Hoboken}"

  def checkincollection(self):
    """
    perform some checks for type incollection
    """
    if self.typ != 'incollection':
      return

    self.placelookup()
    mandatory = ('author', 'year', 'title')
    for m in mandatory:
      self.handleerror(m)
    if self.fields.get('pages') == None: #only check for pages if no electronic journal
      if self.fields.get('url') == None:
        self.fields['pages'] = r"{\biberror{no pages}}"
        self.errors.append("missing pages")
    auth = self.fields.get('author')
    if auth:
      self.addsortname(auth)
    if self.fields.get('crossref'):
      #the content is available in the crossref'd record
      return
    mandatory2 = ['booktitle']
    for m2 in mandatory2:
      self.handleerror(m2)
    if "proceedings" in self.fields.get('booktitle').lower():
      #proceedings often do note have editor, publisher, or address
      return
    mandatory3 = ('editor', 'publisher', 'address')
    for m3 in mandatory3:
      self.handleerror(m3)

  def checkquestionmarks(self):
    """
    check for fields with ??, which are not to be printed
    """
    for field in self.fields:
        if  self.fields[field] != None and '??' in self.fields[field]:
            self.errors.append("?? in %s" % field)

  def handleerror(self,m):
    """
    check whether a mandatory field is present
    replace with error mark if not present
    """
    if self.fields.get(m) == None:
      self.fields[m] = r"{\biberror{no %s}}" % m
      self.errors.append("missing %s"%m)

  def bibtex(self):
    """
    recreate the bibtex record
    output fields will be sorted alphabetically
    remove all fields which are in excludefields
    """
    if self.restrict and self.key not in self.inkeysd:
        return ''
    s = """@%s{%s,\n\t%s\n}"""%(self.typ,
                                self.key,
                                ",\n\t".join(
                                    ["%s = %s" %(f,self.fields[f])
                                    for f in sorted(self.fields.keys())
                                    if f not in excludefields
                                    ]
                                )
        )
    return s



def normalize(s, inkeysd={}, restrict=False):
  a = s.split('\n@')
  #split preamble (if any) from records
  preamble = a[0]
  rest = a[1:]
  #sort and reverse in order to get the order of edited volumes and incollection right
  rest.sort()
  rest = rest[::-1]
  #create the new bibtex records
  bibtexs = [Record(record,
		    fromfile=True,
                    inkeysd=inkeysd,
                    restrict=restrict,
                    reporting=[]
                    ).bibtex()
              for record in rest
            ]
  #assemble output string
  rest = '\n\n'.join([b for b in bibtexs if b])
  return '\n'.join((preamble, rest))

