
from _genotypeparser import GenotypeParser as _GP

def flytuplefromgenotype(string):
    g = _GP(string)
    gt = g.parse()
    short = g.getshortidentifier()
    long_ = g.getlongidentifier()
    tp = gt['type']
    return (tp, short, long_)


