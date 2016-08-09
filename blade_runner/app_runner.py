__author__ = 'hubermant'

class AppRunner(object):
    pass

class Configuration(object):
    pass

class Parameter(object):
    def apply(self):
        pass

class RangeParameter(Parameter):
    def __init__(self, start, end, interval):
        self.start = start
        self.end = end
        self.interval = interval

    def apply(self):
        return xrange(self.start,self.end,self.interval)



class ListParameter(Parameter):
    pass
