#!/usr/bin/env python
import math
import random

class KNN():
    def __init__(self, data):
        self.data = data

    def __euclidean(self, v1, v2):
        distance = 0.0
        for i in range(min(len(v1), len(v2))):
            distance += (v1[i] - v2[i]) ** 2
        return math.sqrt(distance)

    def __getDistance(self, vector):
        distances = []
        for k, v in self.data.items():
            distances.append((self.__euclidean(vector, v['input']), k))
        distances.sort()
        return distances

    def normalWeight(self, distance):
        return 1

    def inverseWeight(self, distance, num = 1.0, const = 0.1):
        return num / (distance + const)

    def subtractWeight(self, distance, const = 1.0):
        if distance > const:
            return 0
        else:
            return const - distance

    def gaussianWeight(self, distance, sigma = 10.0):
        power = math.pow(distance, 2) / (2 * math.pow(sigma, 2))
        return 1 / math.pow(math.e, min(709, power))

    def estimate(self, v1, k = 5, function = None):
        if not function:
            function = self.normalWeight

        distances = self.__getDistance(v1)
        result = []
        for i in range(k):
            result.append((distances[i][1], function(distances[i][0])))
        return result
