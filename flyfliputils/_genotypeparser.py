
import collections
import re

class GenotypeParser(object):

    GRE = re.compile(r"""
        [ ]*                                          # initial white spaces
        (?P<firstChromosome>[a-zA-Z0-9+\-():/, ]*)    # first chromosome
        [ ]*;[ ]*                                     # first seperator
        (?P<secondChromosome>[a-zA-Z0-9+\-():/, ]*)   # second chromosome
        [ ]*;[ ]*                                     # second seperator
        (?P<thirdChromosome>[a-zA-Z0-9+\-():/, ]*)    # third chromosome
        [ ]*;[ ]*                                     # third seperator
        """, re.VERBOSE)

    CRE = re.compile(r"""XXX # use this as a cross seperator""", re.VERBOSE)

    SVRE = re.compile(u"\u263f")
    SFRE = re.compile(u"\u2640")
    SMRE = re.compile(u"\u2642")

    def __init__(self, string):
        self.string = string

        if self.isCross():
            self.fly0 = True
            self.fly1 = True
        else:
            self.fly0 = True
            self.fly1 = False


    def _getflies(self):
        return re.split(self.CRE, self.string)


    def isCross(self):
        flies = self._getflies()
        if len(flies) == 1:
            return False
        elif len(flies) == 2:
            return True
        else:
            raise Exception("There's something wrong with %s" % g)

    
    def getGender(self, index):
        fly = self._getflies()[index]
        if re.search(self.SVRE, fly):
            return 'virgin'
        elif re.search(self.SMRE, fly):
            return 'male'
        elif re.search(self.SFRE, fly):
            return 'female'
        else:
            return 'N/A'


    def getGenotype(self, index):
        fly = self._getflies()[index]
        m = self.GRE.match(fly)
        chromosomes = [ m.group('firstChromosome'),
                        m.group('secondChromosome'),
                        m.group('thirdChromosome') ]
        cs = {}
        for i,c in enumerate(chromosomes):
            _tmp = sorted(map(lambda x: x.strip(), c.split('/')))
            homozygous = False if len(_tmp) == 2 else True
            cs[i+1] = {}
            cs[i+1]['homozygous'] = homozygous
            cs[i+1]['allele0'] = _tmp[0]
            cs[i+1]['allele1'] = _tmp[0 if homozygous else 1]

        return cs
            

    def parse(self):
        ret = {}
        ret['type'] = 'cross' if self.isCross() else 'stock'
        ret['fly0'] = {'gender' : self.getGender(0),
                       'genotype': self.getGenotype(0)}
        if self.isCross():
            ret['fly1'] = {'gender' : self.getGender(1),
                           'genotype': self.getGenotype(1)}
        else:
            ret['fly1'] = ret['fly0']
        return ret


    def getshortidentifier(self):
        """This function tries to return a short identifier for the stock or cross.

        it is not garantied to be unique, or readable :)
        """
        gt = self.parse()
        if gt['type'] == 'stock':
            return self._getshortidentifierfromfly(gt['fly0'])
        elif gt['type'] == 'cross':
            return ( self._getshortidentifierfromfly(gt['fly0']) + ' X ' +
                     self._getshortidentifierfromfly(gt['fly1']) )


        
    def _getshortidentifierfromfly(self, gt):
        # just use 2nd and 3rd chromosome
        alleles2 = [ gt['genotype'][2]['allele0'],
                     gt['genotype'][2]['allele1'] ]
        alleles3 = [ gt['genotype'][3]['allele0'],
                     gt['genotype'][3]['allele1'] ]
        homozyg2 = gt['genotype'][2]['homozygous']
        homozyg3 = gt['genotype'][3]['homozygous']
        
        # get important alleles
        if homozyg2:
            C2 = alleles2[0]
        else:
            C2 = alleles2[0] if alleles2[1] == 'cyo' else alleles2[1]
        if homozyg3:
            C3 = alleles3[0]
        else:
            C3 = alleles3[0] if alleles3[1] == 'Tm3ser' else alleles3[1]
      
        #print ''
        #print 'C2> %s' % C2
        #print 'C3> %s' % C3
        #print ''


        # check if double balanced
        db = ''
        if ( (set(alleles3) == set(['sb','Tm3ser'])) and
                homozyg2 or ('cyo' in alleles2) ):
            db = 'db'
        if ( (set(alleles2) == set(['if','cyo'])) and
                homozyg3 or ('Tm3ser' in alleles3) ):
            db = 'db'
        if ( ('cyo' in alleles2) and ('Tm3ser' in alleles3) ):
            db = 'db'

        # shorten alleles:
        m = re.match(self.SGTRE, C2)
        if m:
            c2i = m.group('ident')
        else:
            # XXX try to find better fallback
            c2i = C2[:3]
        m = re.match(self.SGTRE, C3)
        if m:
            c3i = m.group('ident')
        else:
            # XXX try to find better fallback
            c3i = C3[:3]
        
        if c2i:
            c2i += '2'
        if c3i:
            c3i += '3'
        out = '%s%s%s' % (c2i, c3i, db)
        if not out:
            out = 'WT'
        
        return out


genotype_tests = [
    u'; + / + ; + / + ;',
    u'w+ ; FOO-Bar / cyo ; sb / Tm3ser ;',
    u'w+ ; BAR-FooB2 ; ;',
    u'w- ; ; BAR-Foo1::BAZ42 ;',
    u'w- ; FOO-Bar / cyo ; BAR-Foo / Tm3ser ;',
    u'w- ; FOO-Bar ; BAR-Baz1 ; \u2642 XXX w+; if / cyo; Foo-BAR1 ; \u263f'
    ]


if __name__ == '__main__':

    import pprint

    for g in genotype_tests:
        print '>> parse', g, '?'
        d = GenotypeParser(g).parse()
        print '------------------------------------'
        pprint.pprint(d)



