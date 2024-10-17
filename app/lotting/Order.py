import numpy as np


class Order:
    def __init__(self, x):
        self.index = x[0]
        self.deliveryTime = datetime.date(
            int(x[1][:4]), int(x[1][5:7]), int(x[1][8:10])
        )
        self.classId = x[2]

    def __eq__(self, other):
        return (
            (self.getID() == other.getID())
            and (self.getTime() == other.getTime())
            and (self.getClass() == other.getClass())
        )

    def getTime(self):
        return self.deliveryTime

    def getClass(self):
        return self.classId

    def getID(self):
        return self.index


def timeDif(x: Order, y: Order):
    return x.getTime() - y.getTime()
