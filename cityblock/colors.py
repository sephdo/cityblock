import random

class ColorManagerBase(object):
    @staticmethod
    def woggle(input_int,max_shift=15):
        if input_int < max_shift:
            delta = random.random()
        elif input_int > 255 - max_shift:
            delta = (-1)*random.random()
        else:
            delta = random.random()*2-1
        return int(max_shift*delta + input_int)
    @staticmethod
    def tupwoggle(input_tup,max_shift=15):
        #return input_tup
        if max_shift == 0:
            return input_tup
        output = []
        for input_int in input_tup:
            if input_int < max_shift:
                delta = random.random()
            elif input_int > 255 - max_shift:
                delta = (-1)*random.random()
            else:
                delta = random.random()*2-1
            output.append(int(max_shift*delta + input_int))
        return (output[0],output[1],output[2])
    @staticmethod
    def randColor():
        return (random.randint(0,255),random.randint(0,255),random.randint(0,255))

class ColorManager(ColorManagerBase):
    ROOF = 'ROOF'
    WALL = 'WALL'
    SKY = 'SKY'
    def __init__(self):
        general_pallette = [(72,60,50),(92,82,72),(128,128,128),(105,105,105),(159,129,112),(138,51,36),(149,69,53)]
        rejected = [(76,40,130),]
        self.roof = general_pallette + [(0,65,106),(47, 79, 79)]
        self.wall = general_pallette + [(165, 42, 42)]
        self.sky = [(90,183,247),(0,135,189),(31,117,254),(70,102,255),(21,244,238),(0,183,235),(135,206,235),(135,206,250),(128,218,235),(0,204,255),(0,191,255),(119,181,254),(0,178,228),(140,190,214)]
        self.palletteMap = {'ROOF':self.roof,'WALL':self.wall,'SKY':self.sky}
    def _get(self,pallette,wog=True,max_shift=None):
        color = random.choice(pallette)
        if not wog:
            return color
        elif not max_shift:
            return self.tupwoggle(random.choice(pallette))
        else:
            return self.tupwoggle(random.choice(pallette),max_shift=max_shift)
    def getRoof(self,**kwargs):
        return self._get(self.roof,**kwargs)
    def getWall(self,**kwargs):
        return self._get(self.wall,**kwargs)
    def getSky(self,**kwargs):
        return self._get(self.sky,**kwargs)
    def get(self,key,**kwargs):
        return self._get(self.palletteMap[key],**kwargs)
cm = ColorManager()
