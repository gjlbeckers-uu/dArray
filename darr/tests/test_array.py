import os
import unittest
from pathlib import Path
import tempfile
import shutil

import numpy as np

from darr.array import asarray, create_array, create_basedir, Array, \
    numtypesdescr, truncate_array, delete_array, AppendDataError, \
    numtypedescriptiontxt
from .utils import tempdir


class DarrTestCase(unittest.TestCase):

    def assertArrayIdentical(self, x, y):
        self.assertEqual(x.dtype, y.dtype)
        self.assertEqual(x.shape, y.shape)
        self.assertEqual(np.sum(x-y), 0)

class AsArray(DarrTestCase):

    def setUp(self):
        self.tempdirname1 = tempfile.mkdtemp()
        self.tempdirname2 = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdirname1)
        shutil.rmtree(self.tempdirname2)


    def check_arrayequaltoasarray(self, ndarray):
        """Tests if asarray creates an array of same shape and dtype and same
        contents as input."""
        dar = asarray(path=self.tempdirname1, array=ndarray, overwrite=True)
        ndarray = np.asarray(ndarray) # could be list or tuple
        self.assertArrayIdentical(dar[:], ndarray)
        self.assertEqual(dar.dtype, ndarray.dtype)
        self.assertEqual(dar.shape, ndarray.shape)

    def test_asarraynumberint(self):
        dar = asarray(path=self.tempdirname1, array=1, overwrite=True)
        self.assertEqual(dar[0], 1)

    def test_asarraynumberfloat(self):
        dar = asarray(path=self.tempdirname1, array=1.0, overwrite=True)
        self.assertEqual(dar[0], 1.0)

    def test_asarrayonedimensionalndarray(self):
        ndarray = np.arange(24)
        self.check_arrayequaltoasarray(ndarray)

    def test_asarraytwodimensionalndarray(self):
        ndarray = np.arange(24).reshape(12, 2)
        self.check_arrayequaltoasarray(ndarray)

    def test_asarraythreedimensionalndarray(self):
        ndarray = np.arange(24).reshape(4, 2, 3)
        self.check_arrayequaltoasarray(ndarray)

    def test_asarrayonedimensionallist(self):
        ndarray = [1, 2, 3, 4]
        self.check_arrayequaltoasarray(ndarray)

    def test_asarraytwodimensionallist(self):
        ndarray = [[1, 2, 3, 4],
                   [1, 2, 3, 4]]
        self.check_arrayequaltoasarray(ndarray)

    def test_asarraythreedimensionallist(self):
        ndarray = [[[1, 2, 3, 4],
                    [1, 2, 3, 4]],
                   [[1, 2, 3, 4],
                    [1, 2, 3, 4]]]
        self.check_arrayequaltoasarray(ndarray)

    def test_asarraynumericdtypes(self):
        dtypes = numtypesdescr.keys()
        for dtype in dtypes:
            with self.subTest(dtype=dtype):
                ndarray = np.arange(24, dtype=dtype)
                self.check_arrayequaltoasarray(ndarray)

    def test_asarrayfortranorder(self):
        ndarray = np.asarray(np.arange(24, dtype='float64'), order='F')
        self.check_arrayequaltoasarray(ndarray)

    def test_asarraycorder(self):
        ndarray = np.asarray(np.arange(24, dtype='float64'), order='C')
        self.check_arrayequaltoasarray(ndarray)

    def test_asarraylittleendian(self):
        ndarray = np.arange(24, dtype='<f4')
        self.check_arrayequaltoasarray(ndarray)

    def test_asarraybigendian(self):
        ndarray = np.arange(24, dtype='>f4')
        self.check_arrayequaltoasarray(ndarray)

    def test_asarrayoverwrite(self):
        a = np.zeros((5,), dtype='float64')
        _ = asarray(path=self.tempdirname1, array=a, overwrite=True)
        b = np.ones((4,2), dtype='uint8')
        dar = asarray(path=self.tempdirname1, array=b, overwrite=True)
        self.assertArrayIdentical(dar[:], b)

    def test_asarraysequencesmallchunklen(self):
        a = [1, 2, 3, 4, 5]
        dar = asarray(path=self.tempdirname1, array=a, chunklen=3,
                      overwrite=True)
        self.assertArrayIdentical(np.array(a), dar[:])

    def test_asarraywritingsmallerchunks(self):
        a = np.arange(1024, dtype='int64').reshape(2,-1)
        dar = asarray(path=self.tempdirname1, array=a, chunklen=4, overwrite=True)
        self.assertArrayIdentical(a, dar[:])
        dar = asarray(path=self.tempdirname1, array=a, chunklen=5, overwrite=True)
        self.assertArrayIdentical(a, dar[:])

    def test_asarraywritinglargerthanlenchunks(self):
        a = np.arange(1024, dtype='int64').reshape(2, -1)
        dar = asarray(path=self.tempdirname1, array=a, chunklen=4096, overwrite=True)
        self.assertArrayIdentical(a, dar[:])

    def test_asarrayarray(self):
        a = np.arange(1024, dtype='int64').reshape(2, -1)
        dar1 = asarray(path=self.tempdirname1, array=a, overwrite=True)
        dar2 = asarray(path=self.tempdirname2, array=a, chunklen=5, overwrite=True)
        self.assertArrayIdentical(dar1[:], dar2[:])

    def test_asarraywronginput(self):
        a = 'text'
        self.assertRaises(TypeError, asarray, path=self.tempdirname1, array=a,
                          chunklen=32, overwrite=True)

    def test_asarraykeepattrs(self):
        class AttrList(list):
            attrs = {'a': 1, 'b': 2}
        a = AttrList([0, 0, 0, 0])
        dar = asarray(path=self.tempdirname1, array=a, overwrite=True)
        self.assertEqual(dict(dar.metadata), AttrList.attrs)

    def test_asarraywarnsnondictattrs(self):
        class AttrList(list):
            attrs = [0]
        a = AttrList([0, 0, 0, 0])
        self.assertWarns(UserWarning, asarray, path=self.tempdirname1, array=a,
                         overwrite=True)

    def test_asarrayfromincompatipletype(self):
        a = {'a': 1}
        self.assertRaises(TypeError, asarray,path=self.tempdirname1, array=a,
                         overwrite=True)

    def test_asarrayarratosamepath(self):
        dar = asarray(path=self.tempdirname1, array=[0,1], overwrite=True)
        self.assertRaises(ValueError, asarray, path=self.tempdirname1,
                          array=dar, overwrite=True)

    def test_asarraysequenceofzerodimnumpyscalars(self):

        def a():
            yield np.float32(0)
            yield np.float32(1)
            yield np.float32(2)

        dar = asarray(path=self.tempdirname1, array=a(), overwrite=True)
        self.assertArrayIdentical(dar[:], np.array([0,1,2], dtype=np.float32))

    def test_asarrayremoveoldmetadata(self):

        dar = asarray(path=self.tempdirname1, array=[1,2],
                      metadata={'a':1}, overwrite=True)
        dar = asarray(path=self.tempdirname1, array=[1, 2],
                      overwrite=True)
        self.assertDictEqual(dict(dar.metadata), {})


class CreateDiskArray(DarrTestCase):

    def check_arrayequaltocreatearray(self, ndarray, shape, dtype=None,
                                      chunklen=None):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=shape,
                               dtype=dtype, chunklen=chunklen,
                               overwrite=True)
            if dtype is not None:
                ndarray = ndarray.astype(dtype)
            self.assertArrayIdentical(ndarray, dar[:])
            self.assertEqual(shape, dar.shape)

    def test_zerosfloat64default(self):
        shape = (12,)
        ndarray = np.zeros(shape, dtype='float64')
        self.check_arrayequaltocreatearray(ndarray=ndarray, shape=shape)

    def test_twodimensional(self):
        shape = (12, 2)
        ndarray = np.zeros(shape, dtype='float64')
        self.check_arrayequaltocreatearray(ndarray=ndarray, shape=shape)

    def test_threedimensional(self):
        shape = (4, 2, 3)
        ndarray = np.zeros(shape, dtype='float64')
        self.check_arrayequaltocreatearray(ndarray=ndarray, shape=shape)

    # split out manually?
    def test_numericdtypes(self):
        dtypes = numtypesdescr.keys()
        for dtype in dtypes:
            ndarray = np.zeros(24, dtype=dtype)
            self.check_arrayequaltocreatearray(ndarray=ndarray, shape=(24,),
                                               dtype=dtype)

    def test_emptyarray(self):
        ndarray = np.zeros(0, dtype='float64')
        self.check_arrayequaltocreatearray(ndarray=ndarray, shape=(0,),
                                           dtype='float64')

    def test_emptyarraymd(self):
        ndarray = np.zeros((0,3,7), dtype='float64')
        self.check_arrayequaltocreatearray(ndarray=ndarray, shape=(0, 3, 7),
                                           chunklen=1)

    def test_emptyarraydifferentdtype(self):
        ndarray = np.zeros(0, dtype='float64')
        self.check_arrayequaltocreatearray(ndarray=ndarray, shape=(0,),
                                           dtype='int64')

    def test_chunked(self):
        ndarray = np.zeros(12, dtype='float64')
        for chunklen in (1, 5, 6, 11, 12, 13):
            self.check_arrayequaltocreatearray(ndarray=ndarray, shape=(12,),
                                               chunklen=chunklen)
        ndarray = np.zeros(13, dtype='float64')
        for chunklen in (1, 6, 7, 12, 13, 14):
            self.check_arrayequaltocreatearray(ndarray=ndarray, shape=(13,),
                                               chunklen=chunklen)

    def test_chunkedthreedimensional(self):
        ndarray = np.zeros((12,3,7), dtype='float64')
        for chunklen in (1, 5, 6, 11, 12, 13):
            self.check_arrayequaltocreatearray(ndarray=ndarray, shape=(12, 3, 7),
                                               chunklen=chunklen*21)
        ndarray = np.zeros((13,3,7), dtype='float64')
        for chunklen in (1, 6, 7, 12, 13, 14):
            self.check_arrayequaltocreatearray(ndarray=ndarray, shape=(13, 3, 7),
                                               chunklen=chunklen*21)

    def test_toosmallchunklen(self):
        ndarray = np.zeros((12, 3, 7), dtype='float64')
        self.check_arrayequaltocreatearray(ndarray=ndarray, shape=(12, 3, 7),
                                           chunklen=1)

    def test_shapeisint(self):
        # we allow shapes to be integers
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=1,
                               dtype='int32', overwrite=True)
            self.assertTupleEqual((1,), dar.shape)

    def test_fillandfillfuncisnotnone(self):
        fillfunc= lambda i: i * 2
        with tempdir() as dirname:
            self.assertRaises(ValueError, create_array, path=dirname,
                              shape=(1,), fill=1, fillfunc=fillfunc,
                              dtype='int32', overwrite=True)


class TestArray(DarrTestCase):

    def setUp(self):
        self.temparpath = tempfile.mkdtemp()
        self.tempnonarpath = tempfile.mkdtemp()
        self.tempar = create_array(path=self.temparpath, shape=(12,),
                                   dtype='int64', metadata={'a': 1},
                                   overwrite=True)

    def tearDown(self):
        shutil.rmtree(str(self.temparpath))
        shutil.rmtree(str(self.tempnonarpath))

    def test_instantiatefromexistingpath(self):
        Array(path=self.temparpath)

    def test_instantiatefromnonexistingpath(self):
       with self.assertRaises(OSError):
            Array(path=self.tempnonarpath)

    def test_setvalues(self):
        self.assertArrayIdentical(self.tempar[2:4],
                                  np.array([0,0], dtype=self.tempar.dtype))
        self.tempar[2:4] = 1
        self.assertArrayIdentical(self.tempar[2:4],
                                  np.array([1, 1], dtype=self.tempar.dtype))

    def test_str(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', overwrite=True)
            self.assertEqual(str(dar),'[0 0]')

    def test_repr(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', overwrite=True)
            # linux and windows have different numpy memmap reprs...
            self.assertEqual(repr(dar)[:18], 'darr array ([0, 0]')

    def test_setaccessmode(self):
        self.assertEqual(self.tempar.accessmode, 'r+')
        self.tempar.accessmode = 'r'
        self.assertEqual(self.tempar.accessmode, 'r')
        self.assertRaises(ValueError, setattr, self.tempar, 'accessmode', 'w')
        self.assertRaises(ValueError, setattr, self.tempar, 'accessmode', 'a')

    def test_itemsize(self):
        self.assertEqual(self.tempar.itemsize, 8)

    def test_nbytes(self):
        self.assertEqual(self.tempar.nbytes, 12*8)

    def test_mb(self):
        self.assertEqual(self.tempar.mb, 12*8/1e6)

    def test_size(self):
        self.assertEqual(self.tempar.size, 12)

    def test_copy(self):
        dar2 = self.tempar.copy(path=self.tempnonarpath, overwrite=True)
        self.assertArrayIdentical(self.tempar[:], dar2[:])
        self.assertEqual(dict(self.tempar.metadata), dict(dar2.metadata))


class TestReadArrayDescr(DarrTestCase):

    def test_arrayinfomissingfile(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', overwrite=True)
            dar._arraydescrpath.unlink()
            self.assertRaises(FileNotFoundError, Array, dar.path)

    def test_arrayinfonewerversionfile(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', overwrite=True)
            arrayinfo = dar._arrayinfo.copy()
            vs = f"1{arrayinfo['darrversion']}"
            arrayinfo['darrversion'] = vs
            dar._write_jsondict(dar._arraydescrfilename, arrayinfo,
                                overwrite=True)
            self.assertWarns(UserWarning, Array, dar.path)

    def test_arrayinfowrongshapetype(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', overwrite=True)
            arrayinfo = dar._arrayinfo.copy()
            arrayinfo['shape'] = ['a', 3]
            dar._write_jsondict(dar._arraydescrfilename, arrayinfo,
                                overwrite=True)
            self.assertRaises(TypeError, Array, dar.path)

    def test_arrayinfowrongorder(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', overwrite=True)
            arrayinfo = dar._arrayinfo.copy()
            arrayinfo['arrayorder'] = 'D'
            dar._write_jsondict(dar._arraydescrfilename, arrayinfo,
                                overwrite=True)
            self.assertRaises(ValueError, Array, dar.path)
            arrayinfo['arrayorder'] = '[D]'
            dar._write_jsondict(dar._arraydescrfilename, arrayinfo,
                                overwrite=True)
            self.assertRaises(Exception, Array, dar.path)

    def test_allowfortranorder(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,4), fill=0,
                               dtype='int64', overwrite=True)
            dar._update_jsondict(dar._arraydescrpath.absolute(),
                                 {'arrayorder': 'F'})
            dar = Array(dirname)
            self.assertIn("Column-major", numtypedescriptiontxt(dar))

    def test_warnwritefortranarray(self):
        with tempdir() as dirname1, tempdir() as dirname2:
            dar = create_array(path=dirname1, shape=(2, 4), fill=0,
                               dtype='int64', overwrite=True)
            dar._update_jsondict(dar._arraydescrpath.absolute(),
                                 {'arrayorder': 'F'})
            dar = Array(dirname1)
            self.assertWarns(UserWarning, asarray, path=dirname2, array=dar,
                             overwrite=True)

class TestConsistency(DarrTestCase):

    def test_consistencycorrect(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', overwrite=True)
            self.assertIsNone(dar._check_consistency())
            dar.append([0,0])
            self.assertIsNone(dar._check_consistency())

    def test_consistencyincorrectinfoshape(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', overwrite=True)
            dar._arrayinfo['shape'] = (3,)
            self.assertRaises(ValueError, dar._check_consistency)

    def test_consistencywronginfoitemsize(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', overwrite=True)
            dar._arrayinfo['numtype'] = 'int32'
            self.assertRaises(ValueError, dar._check_consistency)

    def test_consistencyincorrectinfofileshape(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', overwrite=True)
            arrayinfo = dar._arrayinfo.copy()
            arrayinfo['shape'] = (3,)
            dar._write_jsondict(dar._arraydescrfilename, arrayinfo,
                                overwrite=True)
            self.assertRaises(ValueError, dar._check_consistency)
            self.assertRaises(ValueError, Array, dar.path)

    def test_consistencywronginfofileitemsize(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', overwrite=True)
            arrayinfo = dar._arrayinfo.copy()
            arrayinfo['numtype'] = 'int32'
            dar._write_jsondict(dar._arraydescrfilename, arrayinfo,
                                overwrite=True)
            self.assertRaises(ValueError, dar._check_consistency)
            self.assertRaises(ValueError, Array, dar.path)

class TestCheckArraywriteable(DarrTestCase):

    def test_check_arraywriteable(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', accessmode='r+', overwrite=True)
            self.assertIsNone(dar.check_arraywriteable())

    def test_check_arraynotwriteable(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(2,), fill=0,
                               dtype='int64', accessmode='r', overwrite=True)
            self.assertRaises(OSError, dar.check_arraywriteable)


class IterView(DarrTestCase):

    def setUp(self):
        self.tempearpath = tempfile.mkdtemp() # even array
        self.tempoarpath = tempfile.mkdtemp()  # odd array
        self.tempnonarpath = tempfile.mkdtemp()
        self.tempear = create_array(path=self.tempearpath, shape=(12,),
                                    dtype='int64', metadata={'a': 1},
                                    overwrite=True)
        self.tempoar = create_array(path=self.tempearpath, shape=(13,),
                                    dtype='int64', metadata={'a': 1},
                                    overwrite=True)

    def tearDown(self):
        shutil.rmtree(str(self.tempearpath))
        shutil.rmtree(str(self.tempoarpath))
        shutil.rmtree(str(self.tempnonarpath))

    def test_defaultparams_fit(self):
        l = [c for c in self.tempear.iterview(chunklen=2)]
        self.assertEqual(len(l), 6)
        self.assertArrayIdentical(np.concatenate(l), self.tempear[:])


    def test_remainderfalse_fit(self):
            l = [c for c in self.tempear.iterview(chunklen=2,
                                                  include_remainder=False)]
            self.assertEqual(len(l), 6)
            self.assertArrayIdentical(np.concatenate(l), self.tempear[:])

    def test_defaultparams_nofit(self):
            l = [c for c in self.tempoar.iterview(chunklen=2)]
            self.assertEqual(len(l), 7)
            self.assertArrayIdentical(np.concatenate(l), self.tempoar[:])

    def test_remainderfalse_nofit(self):
            l = [c for c in
                 self.tempoar.iterview(chunklen=2, include_remainder=False)]
            self.assertEqual(len(l), 6)
            self.assertArrayIdentical(np.concatenate(l), self.tempoar[:12])


class AppendData(DarrTestCase):

    def setUp(self):
        self.temparpath = tempfile.mkdtemp() # even array

    def tearDown(self):
        shutil.rmtree(str(self.temparpath))

    def test_appendnumber(self):
        dar = create_array(path=self.temparpath, shape=(2,),
                           dtype='int64', overwrite=True)
        dar.append(1)
        self.assertArrayIdentical(np.array([0, 0, 1], dtype='int64'), dar[:])

    def test_appendlist1d(self):
        dar = create_array(path=self.temparpath, shape=(2,),
                           dtype='int64', overwrite=True)
        dar.append([1,2])
        dar.append([3])
        self.assertArrayIdentical(np.array([0, 0, 1, 2, 3], dtype='int64'), dar[:])

    def test_appendlist2d(self):
        dar = create_array(path=self.temparpath, shape=(2, 3),
                           dtype='int64', overwrite=True)
        dar.append([[1,2,3]])
        dar.append([[1,2,3],[4,5,6]])
        self.assertArrayIdentical(np.array([[0, 0, 0], [0, 0, 0], [1, 2, 3], [1, 2, 3],
                                            [4, 5, 6]], dtype='int64'), dar[:])

    def test_appendtoempty1d(self):
        dar = create_array(path=self.temparpath, shape=(0,),
                           dtype='int64', overwrite=True)
        dar.append([1, 2, 3])
        self.assertArrayIdentical(np.array([1, 2, 3], dtype='int64'), dar[:])

    def test_appendtoempty2d(self):
        dar = create_array(path=self.temparpath, shape=(0, 2),
                           dtype='int64', overwrite=True)
        dar.append([[1,2]])
        dar.append([[1,2],[3,4]])
        self.assertArrayIdentical(np.array([[1, 2], [1, 2], [3, 4]], dtype='int64'),
        dar[:])

    def test_appendempty1d(self):
        dar = create_array(path=self.temparpath, shape=(1,),
                           dtype='int64', overwrite=True)
        dar.append([])
        self.assertArrayIdentical(np.array([0], dtype='int64'), dar[:])

    def test_appendempty2d(self):
        dar = create_array(path=self.temparpath, shape=(1, 2),
                           dtype='int64', overwrite=True)
        dar.append(np.zeros((0,2), dtype='int64'))
        self.assertArrayIdentical(np.array([[0, 0]], dtype='int64'), dar[:])

    def test_appendemptytoempty1d(self):
        dar = create_array(path=self.temparpath, shape=(0,),
                           dtype='int64', overwrite=True)
        dar.append([])
        self.assertArrayIdentical(np.array([], dtype='int64'), dar[:])

    def test_appendemptytoempty2d(self):
        dar = create_array(path=self.temparpath, shape=(0, 2),
                           dtype='int64', overwrite=True)
        dar.append(np.zeros((0, 2), dtype='int64'))
        self.assertArrayIdentical(np.zeros((0, 2), dtype='int64'), dar[:])

    def test_appenddataerror(self):
        def testiter():
            yield [1, 2, 3]
            yield [4, 5, 6]
            raise ValueError
        g = (f for f in testiter())
        dar = create_array(path=self.temparpath, shape=(2,),
                           dtype='int64', overwrite=True)
        self.assertRaises(AppendDataError, dar.iterappend, g)
        self.assertArrayIdentical(dar[:], np.array([0, 0, 1, 2, 3, 4, 5, 6],
                                                   dtype='int64'))

    def test_appendwrongshape(self):
        dar = create_array(path=self.temparpath, shape=(2,3),
                           dtype='int64', overwrite=True)
        ar = [[3,4]]
        self.assertRaises(AppendDataError, dar.append, ar)

    def test_appendreadonlyarray(self):
        dar = create_array(path=self.temparpath, shape=(2,),
                           dtype='int64', overwrite=True, accessmode='r')
        ar = [3, 4]
        self.assertRaises(OSError, dar.append, ar)

    def test_iterappendnoniterable(self):
        dar = create_array(path=self.temparpath, shape=(2,),
                           dtype='int64', overwrite=True)
        ar = 3
        self.assertRaises(TypeError, dar.iterappend, ar)

    # def test_fdclosedduringiterappend(self):
    #
    #     def seq(dar):
    #         yield [0]
    #         dar._valuesfd.close()
    #         yield [0]
    #
    #     dar = create_array(path=self.temparpath, shape=(2,),
    #                        dtype='int64', overwrite=True)
    #     self.assertRaises(AppendDataError, dar.iterappend, seq(dar))
    #     self.assertArrayIdentical(dar, np.array([0, 0, 0], dtype='int64'))
    #     dar._check_consistency()


class TestIterView(DarrTestCase):

    def setUp(self):
        self.temparpath = tempfile.mkdtemp()
        self.tempar = create_array(path=self.temparpath, shape=(10,),
                                   dtype='int64', overwrite=True)

    def tearDown(self):
        shutil.rmtree(str(self.temparpath))

    def test_iterviewstartindextoohigh(self):
        with self.assertRaises(ValueError):
           _ = [f for f in self.tempar.iterview(chunklen=2, startindex=12,
                                                endindex=2)]

    def test_iterviewendindextoohigh(self):
        with self.assertRaises(ValueError):
            _ = [f for f in self.tempar.iterview(chunklen=2, startindex=1,
                                                 endindex=12)]


class MetaData(DarrTestCase):

    def setUp(self):
        self.temparpath = tempfile.mkdtemp() # even array
        self.metadata = md = {'fs':20000, 'x': 33.3}
        self.tempar = create_array(path=self.temparpath, shape=(12,),
                                    dtype='int64', metadata=md,
                                   accessmode='r+', overwrite=True)
    def tearDown(self):
        shutil.rmtree(str(self.temparpath))


    def test_createwithmetadata(self):
        self.assertDictEqual(dict(self.tempar.metadata), self.metadata)

    def test_getmetadata(self):
        self.assertEqual(self.tempar.metadata.get('fs'), 20000)

    def test_metadatavalues(self):
        self.assertEqual(set(self.tempar.metadata.values()), {20000,33.3})


    def test_changemetadata(self):
        self.tempar.metadata['fs'] = 40000
        self.assertDictEqual(dict(self.tempar.metadata), {'fs': 40000, 'x': 33.3})
        self.tempar.metadata.update({'x': 34.4})
        self.assertDictEqual(dict(self.tempar.metadata), {'fs': 40000, 'x': 34.4})

    def test_popmetadata(self):
        self.tempar.metadata.pop('x')
        self.assertDictEqual(dict(self.tempar.metadata), {'fs': 20000})
        self.tempar.metadata.pop('fs')
        self.assertDictEqual(dict(self.tempar.metadata), {})

    def test_popitmemetadata(self):
        k, _ = self.tempar.metadata.popitem()
        keys = self.tempar.metadata.keys()
        self.assertNotIn(k, keys)
        self.tempar.metadata.popitem()
        self.assertEqual(self.tempar._metadata.path.exists(), False)

    def test_metadataaccessmodereadwrite(self):
        self.assertEqual(self.tempar.metadata.accessmode, 'r+')
        self.tempar.metadata['x'] = 22.2

    def test_metadataaccessmodereadonly(self):
        self.tempar.accessmode = 'r'
        self.assertEqual(self.tempar.metadata.accessmode, 'r')
        self.assertRaises(OSError, self.tempar.metadata.popitem)
        self.assertRaises(OSError, self.tempar.metadata.pop)
        self.assertRaises(OSError, self.tempar.metadata.update, {'a': 3})

    def test_setaccessmode(self):
        self.assertEqual(self.tempar.metadata.accessmode, 'r+')
        self.tempar.metadata.accessmode = 'r'
        self.assertEqual(self.tempar.metadata.accessmode, 'r')
        self.assertRaises(ValueError, setattr, self.tempar.metadata,
                          'accessmode', 'w')
        self.assertRaises(ValueError, setattr, self.tempar.metadata,
                          'accessmode', 'a')

    def test_delitem(self):
        del self.tempar.metadata['x']
        self.assertDictEqual(dict(self.tempar.metadata), {'fs': 20000})

    def test_metadatarepr(self):
        self.assertEqual(repr(self.tempar.metadata),
                         "{'fs': 20000, 'x': 33.3}")

    def test_metadatalen(self):
        l = len(self.tempar.metadata)
        self.assertEqual(l, 2)

    def test_metadataitems(self):
        self.assertTupleEqual((('fs', 20000), ('x', 33.3)),
                              tuple(self.tempar.metadata.items()))


class TestOpenFile(DarrTestCase):

    def test_openfile(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(0, 2), dtype='int64',
                               overwrite=True, accessmode='r+')
            with dar.open_file('notes.txt', 'a') as f:
                f.write('test\n')
            path = dar.path / 'notes.txt'
            self.assertEqual(path.exists(), True)

    def test_openfileprotectedfiles(self):
        with tempdir() as dirname:
            dar = create_array(path=dirname, shape=(0, 2), dtype='int64',
                               overwrite=True, accessmode='r+')
            for fn in dar._filenames:
                with self.assertRaises(OSError):
                    with dar.open_file(fn, 'a') as f:
                        f.write('test\n')



class TruncateData(DarrTestCase):

    def test_truncate1d(self):
        with tempdir() as dirname:
            dirname = dirname / 'test'
            a = np.array([0, 1, 2, 3, 4], dtype='int64')
            dar = asarray(path=dirname, array=a, accessmode='r+')
            truncate_array(dar, 2)
            self.assertArrayIdentical(dar[:],
                                      np.array([0,1], dtype=dar.dtype))
            # a = Array(dirname)
            # self.assertArrayIdentical(a[:],
            #                   np.array([0, 1], dtype=a.dtype))

    def test_truncatebydirname(self):
        with tempdir() as dirname:
            dirname = dirname / 'test'
            a = np.array([0, 1, 2, 3, 4], dtype='int64')
            dar = asarray(path=dirname, array=a, accessmode='r+')
            truncate_array(dirname, 2)
            # a = Array(dirname)
            # self.assertArrayIdentical(a[:], np.array([0, 1],
            #                                          dtype=a.dtype))

    def test_donottruncatenondarrdir(self):
        with tempdir() as dirname:
            dirname = dirname / 'test'
            bd = create_basedir(dirname)
            bd._write_jsondict('test.json', {'a': 1})
            self.assertRaises(TypeError, truncate_array, dirname, 3)

    def test_truncateinvalidindextype(self):
        with tempdir() as dirname:
            dirname = dirname / 'test'
            a = np.array([0, 1, 2, 3, 4], dtype='int64')
            dar = asarray(path=dirname, array=a, accessmode='r+')
            self.assertRaises(TypeError, truncate_array, dar, 'a')

    def test_truncateindextoohigh(self):
        with tempdir() as dirname:
            dirname = dirname / 'test'
            a = np.array([0, 1, 2, 3, 4], dtype='int64')
            dar = asarray(path=dirname, array=a, overwrite=True,
                          accessmode='r+')
            self.assertRaises(IndexError, truncate_array, dar, 10)



class DeleteArray(DarrTestCase):

    def test_simpledeletearray(self):
        with tempdir() as dirname:
            dalpath = Path(dirname).joinpath('temp.dal')
            dar = create_array(path=dalpath, shape=(0, 2), dtype='int64')
            delete_array(dar)
            self.assertEqual(len(os.listdir(dirname)), 0)

    def test_simpledeletearraypath(self):
        with tempdir() as dirname:
            dalpath = Path(dirname).joinpath('temp.dal')
            _ = create_array(path=dalpath, shape=(0, 2), dtype='int64')
            delete_array(dalpath)
            self.assertEqual(len(os.listdir(dirname)), 0)

    def test_donotdeletenondarrfile(self):
        with tempdir() as dirname:
            dalpath = Path(dirname).joinpath('temp.dal')
            dar = create_array(path=dalpath, shape=(0, 2), dtype='int64')
            dar._write_jsondict('test.json', {'a': 1})
            testpath = dar._path.joinpath('test.json')
            self.assertRaises(OSError, delete_array, dar)
            self.assertEqual(testpath.exists(), True)

    def test_donotdeletenondarrdir(self):
        with tempdir() as dirname:
            bd = create_basedir(dirname, overwrite=True)
            self.assertRaises(TypeError, delete_array, dirname)
            bd._write_jsondict('test.json', {'a': 1})
            self.assertRaises(TypeError, delete_array, dirname)

if __name__ == '__main__':
    unittest.main()