#!/usr/bin/env python

'''
@package pyon.ion.granule.test.test_record_dictionary
@file pyon/ion/granule/test/test_record_dictionary.py
@author David Stuebe
@author Tim Giguere
@brief https://confluence.oceanobservatories.org/display/CIDev/R2+Construction+Data+Model
'''


import unittest
from nose.plugins.attrib import attr
import numpy
from ion.services.dm.utility.granule.taxonomy import TaxyTool
from ion.services.dm.utility.granule.record_dictionary import RecordDictionaryTool
from coverage_model.parameter import ParameterDictionary, ParameterContext
from coverage_model.parameter_types import QuantityType
from coverage_model.basic_types import AxisTypeEnum

@attr('UNIT', group='dm')
class RecordDictionaryToolTestCase(unittest.TestCase):

    def setUp(self):

        self._tx = TaxyTool()
        self._tx.add_taxonomy_set('temp', 'long_temp_name')
        self._tx.add_taxonomy_set('cond', 'long_cond_name')
        self._tx.add_taxonomy_set('pres', 'long_pres_name')
        self._tx.add_taxonomy_set('rdt')
        self._tx.add_taxonomy_set('rdt2')
        # map is {<local name>: <granule name or path>}

        self._rdt = RecordDictionaryTool(taxonomy=self._tx)

        self._pdict = ParameterDictionary()

        t_ctxt = ParameterContext('time', param_type=QuantityType(value_encoding=numpy.dtype('int64')))
        t_ctxt.reference_frame = AxisTypeEnum.TIME
        t_ctxt.uom = 'seconds since 01-01-1970'
        self._pdict.add_context(t_ctxt)

        lat_ctxt = ParameterContext('lat', param_type=QuantityType(value_encoding=numpy.dtype('float32')))
        lat_ctxt.reference_frame = AxisTypeEnum.LAT
        lat_ctxt.uom = 'degree_north'
        self._pdict.add_context(lat_ctxt)

        lon_ctxt = ParameterContext('lon', param_type=QuantityType(value_encoding=numpy.dtype('float32')))
        lon_ctxt.reference_frame = AxisTypeEnum.LON
        lon_ctxt.uom = 'degree_east'
        self._pdict.add_context(lon_ctxt)

        temp_ctxt = ParameterContext('temp', param_type=QuantityType(value_encoding=numpy.dtype('float32')))
        temp_ctxt.uom = 'degree_Celsius'
        self._pdict.add_context(temp_ctxt)

        cond_ctxt = ParameterContext('conductivity', param_type=QuantityType(value_encoding=numpy.dtype('float32')))
        cond_ctxt.uom = 'unknown'
        self._pdict.add_context(cond_ctxt)

        pres_ctxt = ParameterContext('pres', param_type=QuantityType(value_encoding=numpy.dtype('float32')))
        pres_ctxt.uom = 'unknown'
        self._pdict.add_context(pres_ctxt)

        self._rdt_pdict = RecordDictionaryTool(param_dictionary=self._pdict)

    def test_init(self):

        # initialize with a ParameterDictionary
        rdt = RecordDictionaryTool(param_dictionary=self._pdict)
        self.assertIsInstance(rdt._param_dict, ParameterDictionary)

        # initialize with nonsense
        self.assertRaises(TypeError, RecordDictionaryTool, ['foo', 'barr'])

        # initialize with a valid shape
        rdt = RecordDictionaryTool(param_dictionary=self._pdict, shape=(5,2))
        self.assertEquals(rdt._shp, (5,2))

        rdt = RecordDictionaryTool(param_dictionary=self._pdict, shape=(5,))
        self.assertEquals(rdt._shp, (5,))

        rdt = RecordDictionaryTool(param_dictionary=self._tx, shape=5)
        self.assertEquals(rdt._shp, (5,))

        # initialize with no length
        rdt = RecordDictionaryTool(param_dictionary=self._pdict)
        self.assertEquals(rdt._shp, None)

    def test_init_with_taxonomy(self):

        # initialize with a taxonomy tool
        rdt = RecordDictionaryTool(taxonomy=self._tx)
        self.assertIsInstance(rdt._tx, TaxyTool)

        # initialize with a taxonomy object
        rdt = RecordDictionaryTool(taxonomy=self._tx._t)
        self.assertIsInstance(rdt._tx, TaxyTool)

        # initialize with pooo
        self.assertRaises(TypeError, RecordDictionaryTool, ['foo', 'barr'])

        # initialize with a valid shape
        rdt = RecordDictionaryTool(taxonomy=self._tx, shape=(5,2))
        self.assertEquals(rdt._shp, (5,2))

        rdt = RecordDictionaryTool(taxonomy=self._tx, shape=(5,))
        self.assertEquals(rdt._shp, (5,))

        rdt = RecordDictionaryTool(taxonomy=self._tx, shape=5)
        self.assertEquals(rdt._shp, (5,))

        # initialize with no length
        rdt = RecordDictionaryTool(taxonomy=self._tx)
        self.assertEquals(rdt._shp, None)

    def test_set_and_get(self):
        #make sure you can set and get items in the granule by name in the taxonomy

        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)


        self.assertRaises(KeyError, self._rdt.__setitem__, 'long_temp_name', temp_array)
        self.assertRaises(KeyError, self._rdt.__setitem__, 'nonsense', temp_array)

        self._rdt_pdict['temp'] = temp_array
        self._rdt_pdict['conductivity'] = cond_array
        self._rdt_pdict['pres'] = pres_array

        self.assertTrue(numpy.allclose(self._rdt_pdict['temp'], temp_array))
        self.assertTrue(numpy.allclose(self._rdt_pdict['conductivity'], cond_array))
        self.assertTrue(numpy.allclose(self._rdt_pdict['pres'], pres_array))

        #want to check to make sure a KeyError is raised when a non-nickname key is used, but it's not working correctly
        self.assertRaises(KeyError, self._rdt.__getitem__, 'long_temp_name')
        self.assertRaises(KeyError, self._rdt.__getitem__,'nonsense!')

        pdict =self._pdict
        rdt = RecordDictionaryTool(param_dictionary=pdict)
        rdt['temp'] = temp_array

        # Now test bad values... list not numpy array...
        with self.assertRaises(TypeError) as te:
            rdt['temp'] = [1,2,3]

        self.assertEquals(
            te.exception.message,
            '''Invalid type "<type 'list'>" in Record Dictionary Tool setitem with name "temp". Valid types are numpy.ndarray and RecordDictionaryTool'''
            )

        # Now test numpy scalar array...
        with self.assertRaises(TypeError) as te:
            rdt['temp'] = numpy.float32(3.14159)

        self.assertEquals(
            te.exception.message,
            '''Invalid type "<type 'numpy.float32'>" in Record Dictionary Tool setitem with name "temp". Valid types are numpy.ndarray and RecordDictionaryTool'''
        )


        # Now test rank zero array...
        with self.assertRaises(ValueError) as te:
            rdt['temp'] = numpy.array(22.5)

        self.assertEquals(
            te.exception.message,
            '''The rank of a value sequence array in a record dictionary must be greater than zero. Got name "temp" with rank "0"'''
        )

        #TODO: Fix record_dictionary shape validation, then put this test back in
        # Test set invalid shape
        pres_array = numpy.random.standard_normal(90)
        with self.assertRaises(ValueError) as te:
            rdt['pres'] = pres_array

        self.assertEquals(
            te.exception.message,
            '''Invalid array shape "(90,)" for name "pres"; Record dictionary defined shape is "(100,)"'''
        )


        # make a new RDT for testing higher rank objects...
        rdt = RecordDictionaryTool(param_dictionary=self._pdict)

        # Now test rank 2 array...
        rdt['temp'] = numpy.array([[22.5,],])
        self.assertTrue((rdt['temp'] == numpy.array([[22.5,],])).all())

        # Now test rank 2 array...
        rdt['conductivity'] = numpy.array([[28.5,],])
        self.assertTrue((rdt['conductivity'] == numpy.array([[28.5,],])).all())

    def test_set_and_get_with_taxonomy(self):
        #make sure you can set and get items in the granule by name in the taxonomy

        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)


        self.assertRaises(KeyError, self._rdt.__setitem__, 'long_temp_name',temp_array)
        self.assertRaises(KeyError, self._rdt.__setitem__, 'nonsense',temp_array)

        self._rdt['temp'] = temp_array
        self._rdt['cond'] = cond_array
        self._rdt['pres'] = pres_array

        self.assertTrue(numpy.allclose(self._rdt['temp'], temp_array))
        self.assertTrue(numpy.allclose(self._rdt['cond'], cond_array))
        self.assertTrue(numpy.allclose(self._rdt['pres'], pres_array))

        #want to check to make sure a KeyError is raised when a non-nickname key is used, but it's not working correctly
        self.assertRaises(KeyError, self._rdt.__getitem__, 'long_temp_name')
        self.assertRaises(KeyError, self._rdt.__getitem__,'nonsense!')

        taxy_tool_obj =self._tx
        rdt = RecordDictionaryTool(taxonomy=taxy_tool_obj)
        rdt['temp'] = temp_array
        self._rdt['rdt'] = rdt

        # Now test when the Record Dictionary Tool is created with the Taxonomy object rather than the TaxyTool
        # This can fail if the == method for TaxyTool is implemented incorrectly

        taxonomy_ion_obj = self._tx._t
        rdt2 = RecordDictionaryTool(taxonomy=taxonomy_ion_obj)
        rdt2['temp'] = temp_array
        self._rdt['rdt2'] = rdt2


        # Now test bad values... list not numpy array...
        with self.assertRaises(TypeError) as te:
            rdt2['temp'] = [1,2,3]

        self.assertEquals(
            te.exception.message,
            '''Invalid type "<type 'list'>" in Record Dictionary Tool setitem with name "temp". Valid types are numpy.ndarray and RecordDictionaryTool'''
        )

        # Now test numpy scalar array...
        with self.assertRaises(TypeError) as te:
            rdt2['temp'] = numpy.float32(3.14159)

        self.assertEquals(
            te.exception.message,
            '''Invalid type "<type 'numpy.float32'>" in Record Dictionary Tool setitem with name "temp". Valid types are numpy.ndarray and RecordDictionaryTool'''
        )


        # Now test rank zero array...
        with self.assertRaises(ValueError) as te:
            rdt2['temp'] = numpy.array(22.5)

        self.assertEquals(
            te.exception.message,
            '''The rank of a value sequence array in a record dictionary must be greater than zero. Got name "temp" with rank "0"'''
        )

        #TODO: Fix record_dictionary shape validation, then put this test back in
        # Test set invalid shape
        pres_array = numpy.random.standard_normal(90)
        with self.assertRaises(ValueError) as te:
            rdt2['pres'] = pres_array

        self.assertEquals(
            te.exception.message,
            '''Invalid array shape "(90,)" for name "pres"; Record dictionary defined shape is "(100,)"'''
        )


        # make a new RDT for testing higher rank objects...
        taxy_tool_obj =self._tx
        rdt = RecordDictionaryTool(taxonomy=taxy_tool_obj)

        # Now test rank 2 array...
        rdt['temp'] = numpy.array([[22.5,],])
        self.assertTrue((rdt['temp'] == numpy.array([[22.5,],])).all())

        # Now test rank 2 array...
        rdt['cond'] = numpy.array([[28.5,],])
        self.assertTrue((rdt['cond'] == numpy.array([[28.5,],])).all())


    def test_iteration(self):
        #Test all four iteration methods for items in the granule

        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)

        self._rdt_pdict['temp'] = temp_array
        self._rdt_pdict['conductivity'] = cond_array
        self._rdt_pdict['pres'] = pres_array

        for k, v in self._rdt_pdict.iteritems():
            if k == 'temp':
                self.assertTrue(numpy.allclose(temp_array, v))
            elif k == 'conductivity':
                self.assertTrue(numpy.allclose(cond_array, v))
            elif k == 'pres':
                self.assertTrue(numpy.allclose(pres_array, v))
            else:
                self.assertTrue(False)

        for k in self._rdt_pdict.iterkeys():
            self.assertTrue(k == 'temp' or k == 'conductivity' or k == 'pres')

        for v in self._rdt_pdict.itervalues():
            self.assertTrue(numpy.allclose(temp_array, v) or numpy.allclose(cond_array, v) or numpy.allclose(pres_array, v))

        for k in self._rdt_pdict:
            self.assertTrue(k == 'temp' or k == 'conductivity' or k == 'pres')

    def test_iteration_with_taxonomy(self):
        #Test all four iteration methods for items in the granule

        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)

        self._rdt['temp'] = temp_array
        self._rdt['cond'] = cond_array
        self._rdt['pres'] = pres_array

        for k, v in self._rdt.iteritems():
            if k == 'temp':
                self.assertTrue(numpy.allclose(temp_array, v))
            elif k == 'cond':
                self.assertTrue(numpy.allclose(cond_array, v))
            elif k == 'pres':
                self.assertTrue(numpy.allclose(pres_array, v))
            else:
                self.assertTrue(False)

        for k in self._rdt.iterkeys():
            self.assertTrue(k == 'temp' or k == 'cond' or k == 'pres')

        for v in self._rdt.itervalues():
            self.assertTrue(numpy.allclose(temp_array, v) or numpy.allclose(cond_array, v) or numpy.allclose(pres_array, v))

        for k in self._rdt:
            self.assertTrue(k == 'temp' or k == 'cond' or k == 'pres')

    def test_update(self):
        # Update this granule with the content of another. Assert that the taxonomies are the same...



        pres_array = numpy.random.standard_normal(100)
        self._rdt_pdict['pres'] = pres_array

        rdt2 = RecordDictionaryTool(param_dictionary=self._pdict)
        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)

        rdt2['temp'] = temp_array
        rdt2['conductivity'] = cond_array

        self._rdt_pdict.update(rdt2)

        self.assertIn('pres', self._rdt_pdict)
        self.assertIn('temp', self._rdt_pdict)
        self.assertIn('conductivity', self._rdt_pdict)

        self.assertTrue((self._rdt_pdict['pres'] == pres_array).all())
        self.assertTrue((self._rdt_pdict['conductivity'] == cond_array).all())
        self.assertTrue((self._rdt_pdict['temp'] == temp_array).all())

        self.assertEquals(len(self._rdt_pdict), 3)

    def test_update_with_taxonomy(self):
        # Update this granule with the content of another. Assert that the taxonomies are the same...



        pres_array = numpy.random.standard_normal(100)
        self._rdt['pres'] = pres_array

        rdt2 = RecordDictionaryTool(taxonomy=self._tx)
        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)

        rdt2['temp'] = temp_array
        rdt2['cond'] = cond_array

        self._rdt.update(rdt2)

        self.assertIn('pres', self._rdt)
        self.assertIn('temp', self._rdt)
        self.assertIn('cond', self._rdt)

        self.assertTrue((self._rdt['pres'] == pres_array).all())
        self.assertTrue((self._rdt['cond'] == cond_array).all())
        self.assertTrue((self._rdt['temp'] == temp_array).all())

        self.assertEquals(len(self._rdt), 3)

    def test_len(self):
        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)

        self._rdt_pdict['temp'] = temp_array
        self._rdt_pdict['conductivity'] = cond_array
        self._rdt_pdict['pres'] = pres_array

        self.assertEquals(len(self._rdt_pdict), 3)

    def test_len_with_taxonomy(self):
        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)

        self._rdt['temp'] = temp_array
        self._rdt['cond'] = cond_array
        self._rdt['pres'] = pres_array

        self.assertEquals(len(self._rdt), 3)

    def test_repr(self):
        # Come up with a reasonable string representation of the granule for debug purposes only

        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)

        self._rdt_pdict['temp'] = temp_array
        self._rdt_pdict['conductivity'] = cond_array
        self._rdt_pdict['pres'] = pres_array
        self.assertTrue(len(repr(self._rdt_pdict)) > 0)

    def test_repr_with_taxonomy(self):
        # Come up with a reasonable string representation of the granule for debug purposes only

        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)

        self._rdt['temp'] = temp_array
        self._rdt['cond'] = cond_array
        self._rdt['pres'] = pres_array
        self.assertTrue(len(repr(self._rdt)) > 0)

    def test_delete(self):
        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)

        self._rdt_pdict['temp'] = temp_array
        self._rdt_pdict['conductivity'] = cond_array
        self._rdt_pdict['pres'] = pres_array

        self.assertIn('pres', self._rdt_pdict)
        self.assertIn('temp', self._rdt_pdict)
        self.assertIn('conductivity', self._rdt_pdict)

        del self._rdt_pdict['pres']

        self.assertNotIn('pres', self._rdt_pdict)
        self.assertIn('temp', self._rdt_pdict)
        self.assertIn('conductivity', self._rdt_pdict)

    def test_delete_with_taxonomy(self):
        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)

        self._rdt['temp'] = temp_array
        self._rdt['cond'] = cond_array
        self._rdt['pres'] = pres_array

        self.assertIn('pres', self._rdt)
        self.assertIn('temp', self._rdt)
        self.assertIn('cond', self._rdt)

        del self._rdt['pres']

        self.assertNotIn('pres', self._rdt)
        self.assertIn('temp', self._rdt)
        self.assertIn('cond', self._rdt)

    def test_contains(self):

        # foobar isn't even in the taxonomy!
        self.assertNotIn('foobar', self._rdt_pdict)

        # Temp is in the ParameterDictionary but not the record dictionary
        self.assertNotIn('temp', self._rdt_pdict)


        # Now put in some data and make sure it works...
        temp_array = numpy.random.standard_normal(100)
        self._rdt_pdict['temp'] = temp_array

        self.assertIn('temp', self._rdt_pdict)

    def test_contains_with_taxonomy(self):

        # foobar isn't even in the taxonomy!
        self.assertNotIn('foobar', self._rdt)

        # Temp is in the taxonomy but not the record dictionary
        self.assertNotIn('temp', self._rdt)


        # Now put in some data and make sure it works...
        temp_array = numpy.random.standard_normal(100)
        self._rdt['temp'] = temp_array

        self.assertIn('temp', self._rdt)

    def test_pretty_print(self):
        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)

        self._rdt_pdict['temp'] = temp_array
        self._rdt_pdict['conductivity'] = cond_array
        self._rdt_pdict['pres'] = pres_array

        self.assertGreater(len(self._rdt_pdict.pretty_print()), 0)

    def test_pretty_print_with_taxonomy(self):
        temp_array = numpy.random.standard_normal(100)
        cond_array = numpy.random.standard_normal(100)
        pres_array = numpy.random.standard_normal(100)

        self._rdt['temp'] = temp_array
        self._rdt['cond'] = cond_array
        self._rdt['pres'] = pres_array


        rdt = RecordDictionaryTool(taxonomy=self._tx)
        rdt['rdt'] = temp_array
        self._rdt['rdt'] = rdt

        self.assertGreater(len(self._rdt.pretty_print()), 0)



