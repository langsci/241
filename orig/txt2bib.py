import sys

try:
    from bibtools import Record
except ImportError:
    from langsci.bibtools import Record

filename = sys.argv[1]
lines = open(filename).readlines()
for l in lines:
    if l.strip == "":
        continue
    r = Record(l, fromfile=False)
    print(r.bibstring)
