from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import os

def path():
    return os.path.dirname(__file__)

def parseDate(value):
    return parse(value)

def parseIsoFormat(value):
    return value.isoformat()

def add2Date(dt, value):
    return dt+relativedelta(days=+value)

def listBtw2Dates(d1, d2):
    listOfDays = []
    tmpListDays = []
    _d1 = parse(d1)
    _d2 = parse(d2)
    _d = _d1
    _count = 0
    
    if _d ==_d2:
        tmpListDays.append(_d)
    else:
        while _d < _d2:
            _d = _d1+relativedelta(days=+_count)
            tmpListDays.append(_d)
            _count+=1

    for d in tmpListDays:
        listOfDays.append([d.day, d.month, d.year, d.weekday(), d.strftime("%Y/%m/%d")])
    
    return listOfDays


class SetTaskDates(object):
    def __init__(self):
        tmp = datetime.combine(datetime.today(), time.min)
        self._start = self._finish = self._referenceStartDate =tmp.isoformat()
        self._duration = 1
        self.posX = 0
    
    @property
    def start(self): 
        return self._start
    
    @start.setter
    def start(self, value):
        try:           
            tmp1 = parse(value)
            tmp2 = parse(self._start)
            if tmp1 != tmp2:
                self._start = tmp1.isoformat()
                tmp3 = tmp1 +relativedelta(days=+self._duration)-relativedelta(days=+1)
                self._finish = tmp3.isoformat()
                tmp4 = tmp1-parse(self._referenceStartDate)
                self.posX = tmp4.days
        except:
           print('*** INVALID START DATE***') 

    @property
    def finish(self):
        return self._finish
    
    @finish.setter
    def finish(self, value):
        try:           
            tmp1 = parse(value)
            tmp2 = parse(self._finish)
            tmp3 = parse(self._start)
            if tmp1 != tmp2:
                if tmp1 >= tmp3 :
                    self._finish = tmp1.isoformat()
                    tmp4 = tmp1 - tmp3
                    self._duration = tmp4.days+1
                else:
                    print('***  FINISH < START OR INVALID DATE FORMAT (AAAA-MM-DD) ***') 
        except:
            print('*** INVALID FINISH DATE***')

    @property
    def duration(self):
        return self._duration
    
    @duration.setter
    def duration(self, value):
        if isinstance(value, int):
            if value != self._duration:
                self._duration = value
                tmp1 = parse(self._start)+relativedelta(days=+value)-relativedelta(days=+1)
                self._finish = tmp1.isoformat()
        else:
            print('*** INVALID DURATION DATA ***')

    @property
    def referenceStartDate(self): 
        return self._referenceStartDate
    
    @referenceStartDate.setter
    def referenceStartDate(self, value):
        try:
            tmp1 = parse(value)
            tmp2 = parse(self._referenceStartDate)
            if tmp1 != tmp2:
                self._referenceStartDate = tmp1.isoformat()
                tmp3 = parse(self._start)-tmp1
                self.posX = tmp3.days
        except:
            print('*** INVALID REFERENCE DATE***')
