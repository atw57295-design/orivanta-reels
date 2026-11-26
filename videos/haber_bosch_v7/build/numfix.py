import re
REP=[("February fourteenth","February 14"),("seventy-eight percent","78 percent"),("nineteenth century","19th century"),("eighteen seventy-nine","1879"),("two hundred times","200 times"),
("forty years","40 years"),("twenty thousand","20,000"),("eighty hours","80 hours"),("thirty tonnes","30 tonnes"),("twenty-first century","21st century")]
def fix(t):
    for a,b in REP: t=re.sub(a,b,t,flags=re.I) if a!=a.lower() else t.replace(a,b).replace(a.capitalize(),b)
    t=re.sub(r"\.\.\.\s*"," ",t); return re.sub(r"\s+"," ",t).strip()
