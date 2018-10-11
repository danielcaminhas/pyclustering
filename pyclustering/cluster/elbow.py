"""!

@brief Elbow method to determine the optimal number of clusters for k-means clustering.
@details Implementation based on paper @cite article::cluster::elbow::1.

@authors Andrei Novikov (pyclustering@yandex.ru)
@date 2014-2018
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


from pyclustering.cluster.kmeans import kmeans
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer


class elbow:
    """!
    @brief Class represents Elbow method that is used to find out appropriate amount of clusters in a dataset.
    @details Elbow method performs clustering using K-Means algorithm for each K and estimate clustering results using
              sum of square erros. By default K-Means++ algorithm is used to calculate initial centers that are used by
              K-Means algorithm.

    """

    def __init__(self, data, kmin, kmax, **kwargs):
        """!
        @brief Construct Elbow method.

        @param[in] data (array_like): Input data that is presented as array of points (objects), each point should be represented by array_like data structure.
        @param[in] kmin (int): Minimum amount of clusters that should be considered.
        @param[in] kmax (int): Maximum amount of clusters that should be considered.
        @param[in] **kwargs: Arbitrary keyword arguments (available arguments: 'initializer').

        <b>Keyword Args:</b><br>
            - initializer (callable): Center initializer that is used by K-Means algorithm (by default K-Means++).

        """
        if kmax - kmin < 3:
            raise ValueError("Amount of K (" + str(kmax - kmin) + ") is too small for analysis. "
                             "It is require to have at least three K to build elbow.")

        self.__initializer = kwargs.get('initializer', kmeans_plusplus_initializer)

        self.__data = data
        self.__kmin = kmin
        self.__kmax = kmax

        self.__wce = []
        self.__elbows = []
        self.__kvalue = -1


    def process(self):
        """!
        @brief Performs analysis to find out appropriate amount of clusters.

        """
        for amount in range(self.__kmin, self.__kmax):
            centers = self.__initializer(self.__data, amount).initialize()
            instance = kmeans(self.__data, centers, ccore=False)
            instance.process()

            self.__wce.append(instance.get_total_wce())

        self.__calculate_elbows()
        self.__find_optimal_kvalue()


    def get_amount(self):
        """!
        @brief Returns appropriate amount of clusters.

        """
        return self.__kvalue


    def get_wce(self):
        """!
        @brief Returns list of total within cluster errors for each K-value (kmin, kmin + 1, ..., kmax - 1).

        """

        return self.__wce


    def __calculate_elbows(self):
        """!
        @brief Calculates potential elbows.

        """
        for index_elbow in range(1, len(self.__wce) - 1):
            elbow = self.__wce[index_elbow - 1] + self.__wce[index_elbow + 1]
            self.__elbows.append(elbow)


    def __find_optimal_kvalue(self):
        """!
        @brief Finds elbow and returns corresponding K-value.

        """
        optimal_elbow_value = max(self.__elbows)
        self.__kvalue = self.__elbows.index(optimal_elbow_value) + 1