
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
        
        return {i+1:c for i,c in enumerate(chromosomes)}
            

    def parse(self):
        ret = collections.OrderedDict()
        ret['type'] = 'cross' if self.isCross() else 'stock'
        ret['fly0'] = {'gender' : self.getGender(0),
                       'genotype': self.getGenotype(0)}
        if self.isCross():
            ret['fly1'] = {'gender' : self.getGender(1),
                           'genotype': self.getGenotype(1)}
        else:
            ret['fly1'] = ret['fly0']
        return ret




genotype_tests = [
    u'; + / + ; + / + ;',
    u'w+ ; FOO-Bar1 ; Foo-Bar1::BAZ42 / cyo ;',
    u'w+::(13) ; BAR-Foo ; BAR-Foo::baz2,FOO-Bar / cyo ;',
    u'w- ; + ; BAR-Foo1::BAZ42 / cyo ;'
    u'w- ; FOO-Bar / cyo ; BarFoo-Baz1 / Tm3ser ; \u2642 XXX w+; if / cyo; Foo-BAR1 ; \u263f'
    ]


if __name__ == '__main__':

    for g in genotype_tests:
        print '>> parse', g, '?'
        d = GenotypeParser(g).parse()
        print '------------------------------------'
        print 'type: %s' % d['type']
        print 'fly0: gender:   %s' % d['fly0']['gender']
        print '      genotype: 1: %s' % d['fly0']['genotype'][1]
        print '                2: %s' % d['fly0']['genotype'][2]
        print '                3: %s' % d['fly0']['genotype'][3]
        print 'fly1: gender:   %s' % d['fly1']['gender']
        print '      genotype: 1: %s' % d['fly1']['genotype'][1]
        print '                2: %s' % d['fly1']['genotype'][2]
        print '                3: %s' % d['fly1']['genotype'][3]
        print ''




