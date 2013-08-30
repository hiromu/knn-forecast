#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import random
import datetime

from knn import KNN

class Forecast():
    def __init__(self, data, testdata = {}, k = 7, function = None, scale = None):
        if scale:
            data = self.rescale(data, scale)
            testdata = self.rescale(testdata, scale)

        self.data = data
        self.testdata = testdata
        self.knn = KNN(data)
        self.k = k

        if function:
            self.function = function
        else:
            self.function = self.knn.inverseWeight

    def rescale(self, data, scale):
        scaledata = {}
        for key in data.keys():
            scaled = [data[key]['input'][i] * scale[i] for i in range(len(scale))]
            scaledata[key] = {'input': scaled, 'result': data[key]['result']}
        return scaledata

    def estimate(self, testdata):
        weathers = {}
        results = self.knn.estimate(testdata, self.k, self.function)
        for result in results:
            weather = self.data[result[0] + datetime.timedelta(hours = 6)]['result']
            if weather not in weathers:
                weathers[weather] = 0
            weathers[weather] += result[1]
        return sorted(weathers.items(), key = lambda x: x[1], reverse = True)
    
    def validation(self, trial = None):
        if not trial:
            trial = 100

        count = 0
        trial = min(trial, len(self.testdata))
        testdata = self.testdata.values()
        random.shuffle(testdata)
    
        for test in testdata[:trial]:
            result = self.estimate(test['input'])
            if result[0][0] == test['result']:
                count += 1
    
        return float(count) / trial
    
    def optimization(self, trial = None, krange = 10):
        best = 0.0
        backup = self.k, self.function
        k, method = None, None
    
        for i in range(1, krange):
            for j in dir(self.knn):
                if not j.endswith('Weight'):
                    continue
    
                self.k, self.function = i, getattr(self.knn, j)
                result = self.validation(trial)
                if result > best:
                    best = result
                    k, method = i, j

                print i, j, best

        self.k, self.function = backup
        return k, method
    
    def testscale(self, scale, trial = None):
        backup = self.data, self.testdata

        self.data, self.testdata = self.rescale(self.data, scale), self.rescale(self.testdata, scale)
        self.knn = KNN(self.data)
        result = self.validation(trial)

        self.data, self.testdata = backup
        self.knn = KNN(self.data)
        return result
    
    def annealing(self, domain, T = 10000, cool = 0.95, step = 1, trial = None, vector = None):
        if not vector:
            vector = [float(random.randint(domain[i][0], domain[i][1])) for i in range(len(domain))]
        best = self.testscale(vector, trial)
        result = vector
        
        while T > 0.1:
            newvec = vector[:]
            i = random.randint(0, len(domain) - 1)
            newvec[i] += random.randint(-step, step)
    
            if newvec[i] < domain[i][0]:
                newvec[i] = domain[i][0]
            elif newvec[i] > domain[i][1]:
                newvec[i] = domain[i][1]
    
            value = self.testscale(newvec, trial)
            p = 1 / pow(math.e, abs(best - value) / T)
            T *= cool
    
            print newvec, value
            if best < value:
                best = value
                result = newvec
            elif random.random() < p:
                vector = newvec
    
        return result
