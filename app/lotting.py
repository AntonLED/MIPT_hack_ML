import numpy as np
import pandas as pd
import datetime
import re
import copy

from Order import Order, timeDif
from Lot import Lot, lotTimeViable, conjugate

def month_iter(start_month, start_year, end_month, end_year):
    start = datetime.datetime(start_year, start_month, 1)
    end = datetime.datetime(end_year, end_month, 1)

    return ((d.month, d.year) for d in rrule(MONTHLY, dtstart=start, until=end))



def lotting(A, Lambda, beta, suppliersIndicators, timeConstraint=30, iterationsAmount=20000, seed=42):
    np.random.seed(seed)
    clusterSize = len(A)
    x_indices = A.index.to_numpy()
    x_dates = A['Срок поставки'].to_numpy()
    x_classes = np.array([classToIndex[i] for i in A['Класс'].to_numpy()])
    x = [(x_indices[i], x_dates[i], x_classes[i]) for i in range(len(A))]
    Ls = [Lot([Order(i)]) for i in x]
    energy = np.sum([1 - Lambda * L.metrics(suppliersIndicators) * len(L) / clusterSize for L in Ls])
    energies = np.zeros(iterationsAmount)
    energiesTrue = np.zeros(iterationsAmount)
    if clusterSize == 1:
        return Ls
    for i in range(iterationsAmount):
        energies[i] = energy
        length = len(Ls)
        conjunction = np.random.choice([False, True])
        if i < iterationsAmount / 10:
            conjunction = True
        if conjunction and (length >= 2):
            k, l = np.random.choice(range(length), size=2, replace=False)
            L1 = Ls[k]
            L2 = Ls[l]
            if lotTimeViable(L1, L2, timeConstraint):
                L3 = Lot(L1.getXs() + L2.getXs())
                e1 = 1 - Lambda * L1.metrics(suppliersIndicators) * len(L1) / clusterSize
                e2 = 1 - Lambda * L2.metrics(suppliersIndicators) * len(L2) / clusterSize
                e3 = 1 - Lambda * L3.metrics(suppliersIndicators) * len(L3) / clusterSize
                deltaE = e3 - e2 - e1
                P = np.exp(- beta * deltaE)
                decision = np.random.rand() < P
                if decision:
                    del Ls[max(k, l)]
                    del Ls[min(k, l)]
                    Ls += [L3]
                    energy += deltaE
        else:
            k = np.random.choice(range(length), size=None, replace=False)
            if np.sum(Ls[k].classesVector()) <= 1:
                continue
            divideByClass = np.random.choice([False, True])
            if divideByClass:
                dividerSize = np.random.choice(range(1, np.sum(Ls[k].classesVector())))
                dividerIndices = np.random.choice(np.nonzero(Ls[k].classesVector())[0], size=dividerSize, replace=False)
                newClasses = np.zeros(classesAmount, dtype=bool)
                newClasses[dividerIndices] = True
                e0 = 1 - Lambda * Ls[k].metrics(suppliersIndicators) * len(Ls[k]) / clusterSize
                L2 = Lot(Ls[k].divideByClasses(newClasses))
                e1 = 1 - Lambda * Ls[k].metrics(suppliersIndicators) * len(Ls[k]) / clusterSize
                e2 = 1 - Lambda * L2.metrics(suppliersIndicators) * len(L2) / clusterSize
                deltaE = e1 + e2 - e0
                P = np.exp(- beta * deltaE)
                decision = np.random.rand() < P
                if decision:
                    Ls += [L2]
                    energy += deltaE
                else:
                    Ls[k].add(L2.getXs())
            divideByTime = np.random.choice([False, True])
            if divideByTime and (len(np.unique(Ls[k].getTimes())) > 1):
                timeDivider = np.random.choice(np.unique(Ls[k].getTimes()))
                e0 = 1 - Lambda * Ls[k].metrics(suppliersIndicators) * len(Ls[k]) / clusterSize
                L2 = Lot(Ls[k].divideByTime(timeDivider))
                if len(L2) == 0:
                    continue
                e1 = 1 - Lambda * Ls[k].metrics(suppliersIndicators) * len(Ls[k]) / clusterSize
                e2 = 1 - Lambda * L2.metrics(suppliersIndicators) * len(L2) / clusterSize
                deltaE = e1 + e2 - e0
                P = np.exp(- beta * deltaE)
                decision = np.random.rand() < P
                if decision:
                    Ls += [L2]
                    energy += deltaE
                else:
                    Ls[k].add(L2.getXs())
    return Ls
