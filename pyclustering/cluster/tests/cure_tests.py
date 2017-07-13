"""!

@brief Unit-tests for CURE algorithm.

@authors Andrei Novikov (pyclustering@yandex.ru)
@date 2014-2017
@copyright GNU Public License

@cond GNU_PUBLIC_LICENSE
    PyClustering is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    PyClustering is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
@endcond

"""


import unittest;

from pyclustering.samples.definitions import SIMPLE_SAMPLES, FCPS_SAMPLES;

from pyclustering.utils import read_sample;

from pyclustering.cluster.cure import cure;

from pyclustering.cluster.encoder import type_encoding, cluster_encoder;

from random import random;


class Test(unittest.TestCase):
    def template_cluster_allocation(self, path, cluster_sizes, number_cluster, number_represent_points = 5, compression = 0.5, ccore_flag = False):
        sample = read_sample(path);
         
        cure_instance = cure(sample, number_cluster, number_represent_points, compression, ccore = ccore_flag);
        cure_instance.process();
         
        clusters = cure_instance.get_clusters();
        representors = cure_instance.get_representors();
        means = cure_instance.get_means();
 
        assert len(clusters) == number_cluster;
        assert len(representors) == number_cluster;
        assert len(means) == number_cluster;
         
        obtained_cluster_sizes = [len(cluster) for cluster in clusters];
         
        total_length = sum(obtained_cluster_sizes);
        assert total_length == len(sample);
         
        cluster_sizes.sort();
        obtained_cluster_sizes.sort();
        assert cluster_sizes == obtained_cluster_sizes;
 
    def testClusterAllocationSampleSimple1(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE1, [5, 5], 2);
     
    def testClusterAllocationSampleSimple1ByCore(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE1, [5, 5], 2, 5, 0.5, True);
     
    def testClusterAllocationSampleSimple2(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE2, [10, 5, 8], 3);
 
    def testClusterAllocationSampleSimple2ByCore(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE2, [10, 5, 8], 3, 5, 0.5, True);
 
    def testClusterAllocationSampleSimple3(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE3, [10, 10, 10, 30], 4);
 
    def testClusterAllocationSampleSimple3ByCore(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE3, [10, 10, 10, 30], 4, 5, 0.5, True);
 
    def testClusterAllocationSampleSimple4(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE4, [15, 15, 15, 15, 15], 5);
 
    def testClusterAllocationSampleSimple4ByCore(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE4, [15, 15, 15, 15, 15], 5, 5, 0.5, True);
 
    def testClusterAllocationSampleSimple5(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE5, [15, 15, 15, 15], 4);
 
    def testClusterAllocationSampleSimple5ByCore(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE5, [15, 15, 15, 15], 4, 5, 0.5, True);
 
    def testClusterAllocationSampleTwoDiamonds(self):
        self.template_cluster_allocation(FCPS_SAMPLES.SAMPLE_TWO_DIAMONDS, [400, 400], 2, 5, 0.3);
 
    def testClusterAllocationSampleTwoDiamondsByCore(self):
        self.template_cluster_allocation(FCPS_SAMPLES.SAMPLE_TWO_DIAMONDS, [400, 400], 2, 5, 0.3, True);
 
    def testClusterAllocationSampleLsun(self):
        self.template_cluster_allocation(FCPS_SAMPLES.SAMPLE_LSUN, [100, 101, 202], 3, 5, 0.3);
 
    def testClusterAllocationSampleLsunByCore(self):
        self.template_cluster_allocation(FCPS_SAMPLES.SAMPLE_LSUN, [100, 101, 202], 3, 5, 0.3, True);
 
    def testOneClusterAllocation(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE1, [10], 1);
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE2, [23], 1);
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE3, [60], 1);
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE4, [75], 1);
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE5, [60], 1);
 
    def testOneClusterAllocationByCore(self):
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE1, [10], 1, 5, 0.5, True);
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE1, [10], 1, 5, 0.5, True);
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE2, [23], 1, 5, 0.5, True);
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE3, [60], 1, 5, 0.5, True);
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE4, [75], 1, 5, 0.5, True);
        self.template_cluster_allocation(SIMPLE_SAMPLES.SAMPLE_SIMPLE5, [60], 1, 5, 0.5, True);
 
 
    def templateClusterAllocationOneDimensionData(self, ccore_flag):
        input_data = [ [random()] for i in range(10) ] + [ [random() + 3] for i in range(10) ] + [ [random() + 5] for i in range(10) ] + [ [random() + 8] for i in range(10) ];
         
        cure_instance = cure(input_data, 4, ccore = ccore_flag);
        cure_instance.process();
        clusters = cure_instance.get_clusters();
         
        assert len(clusters) == 4;
        for cluster in clusters:
            assert len(cluster) == 10;
 
    def testClusterAllocationOneDimensionData(self):
        self.templateClusterAllocationOneDimensionData(False);
 
    def testClusterAllocationOneDimensionDataByCore(self):
        self.templateClusterAllocationOneDimensionData(True);


    def templateEncoderProcedures(self, ccore_flag):
        sample = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE3);
        
        cure_instance = cure(sample, 4, 5, 0.5, ccore = ccore_flag);
        cure_instance.process();
        
        clusters = cure_instance.get_clusters();
        encoding = cure_instance.get_cluster_encoding();
        
        encoder = cluster_encoder(encoding, clusters, sample);
        encoder.set_encoding(type_encoding.CLUSTER_INDEX_LABELING);
        encoder.set_encoding(type_encoding.CLUSTER_OBJECT_LIST_SEPARATION);
        encoder.set_encoding(type_encoding.CLUSTER_INDEX_LIST_SEPARATION);
        
        assert 4 == len(clusters);

    def testEncoderProcedure(self):
        self.templateEncoderProcedures(False);

    def testEncoderProcedureByCore(self):
        self.templateEncoderProcedures(True);

    def testCoreInterfaceIntInputData(self):
        cure_instance = cure([ [1], [2], [3], [20], [21], [22] ], 2, ccore = True);
        cure_instance.process();
        assert len(cure_instance.get_clusters()) == 2;


if __name__ == "__main__":
    unittest.main();