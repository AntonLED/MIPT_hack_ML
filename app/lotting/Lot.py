import numpy as np
import datetime
import re
import copy

from app.lotting.Order import Order, timeDif

class Lot():
    def __init__(self, xs, suppliers=None):
        self.xs = copy.copy(xs)
        if len(xs) == 0:
            return None
        self.beginDate = min([x.getTime() for x in xs])
        self.endDate = max([x.getTime() for x in xs])
        if (len(xs) == 1):
            self.M = 9.0
        elif (suppliers != None):
            #я не хочу трахаться с мгновенным расчётом метрик для случая, когда входной лист заказов не размера 1...
            self.M = self.metrics(suppliers)
        else:
            self.M = None

    def getOrders(self):
        return self.xs

    def add(self, xs):
        self.beginDate = min(self.beginDate, min([x.getTime() for x in xs]))
        self.endDate = max(self.endDate, max([x.getTime() for x in xs]))
        self.xs += copy.copy(xs)

    def getTimes(self):
        return [x.getTime() for x in self.getXs()]

    def divideByClasses(self, classes):
        indices = []
        xs = []
        for i, x in enumerate(self.getXs()):
            if classes[x.getClass()] == True:
                indices.append(i)
        for index in sorted(indices, reverse=True):
            xs.append(self.getXs()[index])
            del self.xs[index]
        self.beginDate = min(self.beginDate, min([x.getTime() for x in self.getXs()]))
        self.endDate = max(self.endDate, max([x.getTime() for x in self.getXs()]))
        return xs

    def divideByTime(self, date):
        #print(date)
        indices = []
        xs = []
        for i, x in enumerate(self.getXs()):
            #print(x.getTime())
            #print(x.getTime() > date)
            if (x.getTime() >  date):
                indices.append(i)
                #print('a')
        for index in sorted(indices, reverse=True):
            xs.append(self.getXs()[index])
            del self.xs[index]
        self.beginDate = min(self.beginDate, min([x.getTime() for x in self.getXs()]))
        self.endDate = max(self.endDate, max([x.getTime() for x in self.getXs()]))
        #print(xs[0])
        return xs

    def __len__(self):
        return len(self.getXs())

    def getXs(self):
        return copy.copy(self.xs)

    def classesVector(self):
        global classesAmount
        classes = np.zeros(classesAmount, dtype=bool)
        for x in self.getXs():
            classes[x.classId] = True
        return classes

    def similarityToSupplier(self, supplier):
        classes = self.classesVector()
        return np.sum((classes * supplier), axis=-1)
    
    def metrics(self, suppliers):
        if len(self.getXs()) == 0:
            return None
        similarities = self.similarityToSupplier(suppliers) / np.sum(self.classesVector())
        eps = 10e-3
        n05 = np.sum([similarities >= 0.5])
        n08 = np.sum([similarities >= 0.8])
        n10 = np.sum([similarities >= 1 - eps])
        n00 = np.sum([similarities >= eps])
        return (2.0 * n05 + 3.0 * n08 + 4.0 * n10) / n00

    def getDateBoundary(self):
        return [self.beginDate, self.endDate]

    def __eq__(self, other):
        if len(self.getXs()) != len(other.getXs()):
            return False
        else:
            return True

def lotTimeViable(L1, L2, timeConstraint):
    aL1, bL1 = L1.getDateBoundary()
    aL2, bL2 = L2.getDateBoundary()
    a = min(aL1, aL2)
    b = max(bL1, bL2)
    delta = b - a
    return delta.days <= timeConstraint

def conjugate(L1, L2):
    return Lot(L1.getXs().extend(L2.getXs()))
