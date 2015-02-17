'''

Cluster analysis algorithm: CURE

Implementation based on article:
 - S.Guha, R.Rastogi, K.Shim. CURE: An Efficient Clustering Algorithm for Large Databases. 1998.

Copyright (C) 2015    Andrei Novikov (spb.andr@yandex.ru)

pyclustering is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyclustering is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

from decimal import *;

from pyclustering.support import read_sample;
from pyclustering.support import euclidean_distance;
from pyclustering.support import euclidean_distance_sqrt;
from pyclustering.support import draw_clusters;
from pyclustering.support.kdtree import kdtree;

import pyclustering.core.wrapper as wrapper;

class cure_cluster:   
    "Representation of CURE cluster."
    
    def __init__(self, point = None):
        if (point is not None):
            self.points = [ point ];
            self.mean = point;
            self.rep = [ point ];
        else:
            self.points = [ ];
            self.mean = None;
            self.rep = [ ];
            
        self.closest = None;
        self.distance = float('inf');      # calculation of distance is really complexity operation (even square distance), so let's store distance to closest cluster.
        
    def __repr__(self):
        return "%s, %s" % (self.distance, self.points);
        

class cure:
    __pointer_data = None;
    __clusters = None;
    
    __number_cluster = 0;
    __number_represent_points = 0;
    __compression = 0;
    
    __queue = None;
    __tree = None;
    
    __ccore = False;
    
    def __init__(self, data, number_cluster, number_represent_points = 5, compression = 0.5, ccore = False):
        "Constructor of clustering algorithm CURE."
         
        "(in) data                       - input data that is presented as list of points (objects), each point should be represented by list or tuple."
        "(in) number_cluster             - number of clusters that should be allocated."
        "(in) number_represent_points    - number of representation points for each cluster."
        "(in) compression                - coefficient defines level of shrinking of representation points toward the mean of the new created cluster after merging on each step."
        "(in) ccore                      - if True than DLL CCORE (C++ solution) will be used for solving the problem."
        
        self.__pointer_data = data;
        self.__number_cluster = number_cluster;
        self.__number_represent_points = number_represent_points;
        self.__compression = compression;
        
        self.__ccore = ccore;
        
        if (ccore is False):
            self.__create_queue();      # queue
            self.__create_kdtree();     # create k-d tree

    
    def process(self):
        "Performs cluster analysis in line with rules of CURE algorithm. Results of clustering can be obtained using corresponding gets methods."
        
        if (self.__ccore is True):
            self.__clusters = wrapper.cure(self.__pointer_data, self.__number_cluster, self.__number_represent_points, self.__compression);
        else:

            while (len(self.__queue) > self.__number_cluster):
                cluster1 = self.__queue[0];            # cluster that has nearest neighbor.
                cluster2 = cluster1.closest;    # closest cluster.
                
                #print("Merge decision: \n\t", cluster1, "\n\t", cluster2);
                
                self.__queue.remove(cluster1);
                self.__queue.remove(cluster2);
                
                self.__delete_represented_points(cluster1);
                self.__delete_represented_points(cluster2);
        
                merged_cluster = self.__merge_clusters(cluster1, cluster2);
        
                self.__insert_represented_points(merged_cluster);
                
                # Pointers to clusters that should be relocated is stored here.
                cluster_relocation_requests = [];
                
                # Check for the last cluster
                if (len(self.__queue) > 0):
                    merged_cluster.closest = self.__queue[0];  # arbitrary cluster from queue
                    merged_cluster.distance = self.__cluster_distance(merged_cluster, merged_cluster.closest);
                    
                    for item in self.__queue:
                        distance = self.__cluster_distance(merged_cluster, item);
                        # Check if distance between new cluster and current is the best than now.
                        if (distance < merged_cluster.distance):
                            merged_cluster.closest = item;
                            merged_cluster.distance = distance;
                        
                        # Check if current cluster has removed neighbor.
                        if ( (item.closest is cluster1) or (item.closest is cluster2) ):
                            # If previous distance was less then distance to new cluster then nearest cluster should be found in the tree.
                            #print("Update: ", item);
                            if (item.distance < distance):
                                (item.closest, item.distance) = self.__closest_cluster(item, distance);
                                
                                # TODO: investigation of root cause is required.
                                # Itself and merged cluster should be always in list of neighbors in line with specified radius.
                                # But merged cluster may not be in list due to error calculation, therefore it should be added
                                # manually.
                                if (item.closest is None):
                                    item.closest = merged_cluster;
                                    item.distance = distance;
                                
                            # Otherwise new cluster is nearest.
                            else:
                                item.closest = merged_cluster;
                                item.distance = distance;
                            
                            cluster_relocation_requests.append(item);
                        elif (item.distance > distance):
                            item.closest = merged_cluster;
                            item.ditance = distance;
                            
                            cluster_relocation_requests.append(item);
                
                # New cluster and updated clusters should relocated in queue
                self.__insert_cluster(merged_cluster);
                [self.__relocate_cluster(item) for item in cluster_relocation_requests];
        
            # Change cluster representation
            self.__clusters = [ cure_cluster_unit.points for cure_cluster_unit in self.__queue ];
    
    
    def get_clusters(self):
        "Returns list of allocated clusters, each cluster contains indexes of objects in list of data."
        
        return self.__clusters;  
    
    
    def __insert_cluster(self, cluster):
        "Insert cluster to list in line with sequence order (distance). Thus list should be always sorted."
        
        "(in) cluster     - CURE cluster that should be inserted."
        
        for index in range(len(self.__queue)):
            if (cluster.distance < self.__queue[index].distance):
                self.__queue.insert(index, cluster);
                return;
    
        self.__queue.append(cluster);        


    def __relocate_cluster(self, cluster):
        "Relocate cluster in list in line with distance order. Helps list to be sorted."
        
        "(in) cluster     - CURE cluster that should be relocated."
        
        self.__queue.remove(cluster);
        self.__insert_cluster(cluster);


    def __closest_cluster(self, cluster, distance):
        "Returns closest cluster to the specified cluster in line with distance."
        
        "(in) cluster     - CURE cluster for which nearest cluster should be found."
        "(in) distance    - closest distance to the previous cluster."
        
        "Returns tuple (nearest CURE cluster, nearest distance) if nearest cluster has been found, otherwise None is returned."
        
        nearest_cluster = None;
        nearest_distance = float('inf');
        
        for point in cluster.rep:
            # Nearest nodes should be returned (at least it will return itself).
            nearest_nodes = self.__tree.find_nearest_dist_nodes(point, distance);
            for (candidate_distance, kdtree_node) in nearest_nodes:
                if ( (candidate_distance < nearest_distance) and (kdtree_node is not None) and (kdtree_node.payload is not cluster) ):
                    nearest_distance = candidate_distance;
                    nearest_cluster = kdtree_node.payload;
                    
        return (nearest_cluster, nearest_distance);


    def __insert_represented_points(self, cluster):
        "Private function that is used by cure. Insert representation points to the k-d tree."
        
        "(in) cluster    - CURE cluster whose representation points should be inserted."
        
        for point in cluster.rep:
            self.__tree.insert(point, cluster);


    def __delete_represented_points(self, cluster):   
        "Remove representation points of clusters from the k-d tree."
        
        "(in) cluster    - CURE cluster whose representation points should be removed."
        
        for point in cluster.rep:
            self.__tree.remove(point);


    def __merge_clusters(self, cluster1, cluster2):
        "Merges two clusters and returns new merged cluster. Representation points and mean points are calculated for the new cluster."
        
        "(in) cluster1                   - CURE cluster that should be merged with cluster2."
        "(in) cluster2                   - CURE cluster that should be merged with cluster1."
        
        "Returns new merged CURE cluster."
        
        merged_cluster = cure_cluster();
        
        merged_cluster.points = cluster1.points + cluster2.points;
        
        # merged_cluster.mean = ( len(cluster1.points) * cluster1.mean + len(cluster2.points) * cluster2.mean ) / ( len(cluster1.points) + len(cluster2.points) );
        dimension = len(cluster1.mean);
        merged_cluster.mean = [0] * dimension;
        for index in range(dimension):
            merged_cluster.mean[index] = ( len(cluster1.points) * cluster1.mean[index] + len(cluster2.points) * cluster2.mean[index] ) / ( len(cluster1.points) + len(cluster2.points) );
        
        temporary = list(); # TODO: Set should be used in line with specification (article), but list is not hashable object therefore it's impossible to use list in this fucking set!
        
        for index in range(self.__number_represent_points):
            maximal_distance = 0;
            maximal_point = None;
            
            for point in merged_cluster.points:
                minimal_distance = 0;
                if (index == 0):
                    minimal_distance = euclidean_distance(point, merged_cluster.mean);
                    #minimal_distance = euclidean_distance_sqrt(point, merged_cluster.mean);
                else:
                    minimal_distance = euclidean_distance(point, temporary[0]);
                    #minimal_distance = cluster_distance(cure_cluster(point), cure_cluster(temporary[0]));
                    
                if (minimal_distance >= maximal_distance):
                    maximal_distance = minimal_distance;
                    maximal_point = point;
        
            if (maximal_point not in temporary):
                temporary.append(maximal_point);
                
        for point in temporary:
            representative_point = [0] * dimension;
            for index in range(dimension):
                representative_point[index] = point[index] + self.__compression * (merged_cluster.mean[index] - point[index]);
                
            merged_cluster.rep.append(representative_point);
        
        return merged_cluster;


    def __create_queue(self):
        "Private function that is used by cure. Create queue (list) of sorted clusters by distance between them, where first cluster has the nearest neighbor."
        "At the first iteration each cluster contains only one point."
        
        "(in) data        - input data that is presented as list of points (objects), each point should be represented by list or tuple."
        
        "Returns create queue (list) of sorted clusters by distance between them."
        
        self.__queue = [cure_cluster(point) for point in self.__pointer_data];
        
        # set closest clusters
        for i in range(0, len(self.__queue)):
            minimal_distance = float('inf');
            closest_index_cluster = -1;
            
            for k in range(0, len(self.__queue)):
                if (i != k):
                    dist = self.__cluster_distance(self.__queue[i], self.__queue[k]);
                    if (dist < minimal_distance):
                        minimal_distance = dist;
                        closest_index_cluster = k;
            
            self.__queue[i].closest = self.__queue[closest_index_cluster];
            self.__queue[i].distance = minimal_distance;
        
        # sort clusters
        self.__queue.sort(key = lambda x: x.distance, reverse = False);
    

    def __create_kdtree(self):
        "Create k-d tree in line with created clusters. At the first iteration contains all points from the input data set."
        
        "Return k-d tree of representation points of CURE clusters."
        
        self.__tree = kdtree();
        for current_cluster in self.__queue:
            for representative_point in current_cluster.rep:
                self.__tree.insert(representative_point, current_cluster);    


    def __cluster_distance(self, cluster1, cluster2):
        "Return minimal distance between clusters. Representative points are used for that."
        
        "(in) cluster1        - CURE cluster 1."
        "(in) cluster2        - CURE cluster 2."
        
        "Returns Euclidean distance between two clusters that is defined by minimum distance between representation points of two clusters."
        
        distance = float('inf');
        for i in range(0, len(cluster1.rep)):
            for k in range(0, len(cluster2.rep)):
                #dist = euclidean_distance_sqrt(cluster1.rep[i], cluster2.rep[k]);   # Fast mode
                dist = euclidean_distance(cluster1.rep[i], cluster2.rep[k]);        # Slow mode
                if (dist < distance):
                    distance = dist;
                    
        return distance;