# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
import unittest
from georeference.test.utils.process.georeferencertest import GeoreferencerTest
from georeference.test.views.process.georeferenceresourcebygeoreferenceidtest import GeoreferenceResourceTest
from georeference.test.views.process.georeferenceresourcebyobjectidtest import GeoreferenceResourceByObjectIdTest
from georeference.test.views.process.georeferencevalidationtest import GeoreferenceValidationTest
from georeference.test.views.process.georeferenceconfirmtest import GeoreferenceConfirmTest

def test_suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()


    print '========================'
    print 'Run test suite ...'
    print '========================'

    print '========================'
    print 'Run view tests ...'
    suite.addTest(loader.loadTestsFromTestCase(GeoreferenceResourceTest))
    suite.addTest(loader.loadTestsFromTestCase(GeoreferenceResourceByObjectIdTest))
    suite.addTest(loader.loadTestsFromTestCase(GeoreferenceValidationTest))
    suite.addTest(loader.loadTestsFromTestCase(GeoreferenceConfirmTest))
    print '------------------------'

    print 'Run process tests ...'
    suite.addTest(loader.loadTestsFromTestCase(GeoreferencerTest))
    print '------------------------'
    print '========================'
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())