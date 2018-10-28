from collections import namedtuple
import random
from types import SimpleNamespace

from .colors import cm

Point = namedtuple('Point',['x','y'])
Padding = namedtuple('Padding',['top','right','bottom','left'])
class RangeNamespace(SimpleNamespace):
    def __init__(self,*args,**kwargs):
        SimpleNamespace.__init__(self,*args,**kwargs)
        self.__dict__.update(kwargs)
    def __getitem__(self,key):
        return getattr(self,key)
    def __iter__(self):
        return iter(self.__dict__)
    def update(self,data):
        self.__dict__.update(data)
class RandRange:
    def __init__(self,lower,upper,rand=None):
        self.lower = lower
        self.upper = upper
        self.prev = None
        self.frozen = False
        if not rand:
            self._rand = random.randint
        elif rand == 'float':
            self._rand = random.uniform
        elif rand == 'even':
            self._rand = self.randEven
    def freeze(self,value=None):
        if self.frozen and value is None:
            return
        elif not value is None:
            self.prev = value
        elif self.prev is None:
            self.prev = self._rand(self.lower,self.upper)
        self.frozen = True
    def unfreeze(self):
        self.frozen = False
    def rand(self,twin=False):
        #print("RAND",*self,self._rand)
        if self.frozen:
            return self.prev
        elif twin and not self.prev is None:
            return self.prev
        else:
            value = self._rand(self.lower,self.upper)
            self.prev = value
            return value
    def randEven(self,a,b):
        return 2*random.randint(a>>1,b>>1)

class RandList:
    def __init__(self,choices):
        self.choices = choices
        self.prev = None
        self.frozen = False
        
    def freeze(self,value=None):
        if self.frozen and value is None:
            return
        elif not value is None:
            self.prev = value
        elif self.prev is None:
            self.prev = self._rand()
        self.frozen = True
    def unfreeze(self):
        self.frozen = False
    def rand(self,twin=False):
        if self.frozen:
            return self.prev
        elif twin and not self.prev is None:
            return self.prev
        else:
            value = self._rand()
            self.prev = value
            return value
    def _rand(self):
        return random.choice(self.choices)
class RandBool(RandList):
    def __init__(self):
        RandList.__init__(self,[True,False])
class RandColorList(RandList):
    def __init__(self,choices,woggle=True,max_shift=None):
        self.woggle = woggle
        self.max_shift = max_shift
        RandList.__init__(self,choices)
    def _rand(self):
        choice = random.choice(self.choices)
        if self.woggle:
            if self.max_shift:
                return cm.tupwoggle(choice,self.max_shift)
            else:
                return cm.tupwoggle(choice)
        return choice
