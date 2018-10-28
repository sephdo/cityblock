import random
from types import SimpleNamespace

from .colors import cm
from .renderers import Bresenham
from .utils import *
from .sprites import *

class Neighborhood:
    def __init__(self):
        self.ranges = dict(
            HOUSE_COUNT=RandRange(2,10),
            TWIN_THRESHOLD=RandRange(.8,.99,'float'),
            MONO_THRESHOLD=RandRange(.8,.99,'float'),
            WINDOW_LIGHT_PCT=RandRange(.2,.8,'float'), # Should relate to time of day / sky color
            )
        self.colors = dict(
            SKY_PRIMARY=RandColorList(cm.sky),
            SKY_SECONDARY=RandRange(1,3),
            )
        self.image = self.makeNeighborhood()
    def makeNeighborhood(self):
        data = SimpleNamespace(**{key:value.rand() for key,value in self.ranges.items()})
        colors = SimpleNamespace(**{key:value.rand() for key,value in self.colors.items()})

        ## Secondary fields
        if colors.SKY_SECONDARY == 1:
            colors.SKY_SECONDARY = cm.getSky()
        elif colors.SKY_SECONDARY == 2:
            colors.SKY_SECONDARY = colors.SKY_PRIMARY
        else:
            colors.SKY_SECONDARY = cm.tupwoggle(colors.SKY_PRIMARY,45)
        houses = []
        for house,dx,dy in HouseGenerator(data).makeHouses():
            houses.append((house,dx,dy))
        c = Canvas.fromStack(houses,vertical=False,alignment='bottom',pad=(5,5,0,0))
        sky = RectGradient(c.width,c.height,colors.SKY_PRIMARY,colors.SKY_SECONDARY,max_shift=3)
        c = Canvas.fromSprites([(sky,0,0),(c,0,0)])
        #c.export('test.png')
        return c.export()
    def getSky(self,i=None):
        if not i:
            i = random.randint(1,3)
        sky1 = cm.getSky()
        if i == 1:
            sky2 = sky1
        elif i == 2:
            sky2 = cm.getSky()
        elif i == 3:
            sky2 = cm.tupwoggle(sky1,45)
        return sky1,sky2
    def twinRule(self,floorcount):
        return True if random.random() > .45+floorcount/10 else False


class HouseGenerator:
    def __init__(self,neighborhood):
        self.ranges = dict(
            FLOOR_WIDTH=RandRange(36,72),
            FLOOR_HEIGHT=RandRange(20,24),
            FLOOR_COUNT=RandRange(1,5),

            WALL_BORDERS=RandList(['-bottom','top','vertical']),
            WALL_HAS_BORDERS=RandList([True,False,False]),
            
            #WINDOW_WIDTH=RandRange(5,7),
            WINDOW_WIDTH=RandRange(7,9),
            #WINDOW_FLOOR_RATIO=RandRange(.25,.5,'float'),
            WINDOW_FLOOR_RATIO=RandRange(.33,.6,'float'),
            WINDOW_MARGIN=RandList([0,1,1,2,2,3,3,]),
            WINDOW_BORDERS=RandList(['all','vertical','horizontal','bottom']),
            WINDOW_HAS_BORDERS=RandList([True,True,False]),
            WINDOW_DELTA=RandList([1,3]), #Used if window_count is reduced and a large central window is added
            
            ROOF_PITCH=RandRange(.1,.5,'float'),
            ROOF_AWNING=RandRange(0,10,'even'),
            ROOF_TYPE=RandList([SimpleRoof,FlatRoof,NullRoof,StaggeredRoof,FpRoof]),
            #ROOF_TYPE=RandList([FpRoof]),
            ROOF_DIRECTION=RandBool(),
            ROOF_LEVELS=RandRange(2,4),
            ROOF_STEP_LENGTH=RandRange(3,5),
            ROOF_HAS_SURFACE=RandBool(),
            
            )
        self.colors = dict(
            ROOF=RandColorList(cm.roof),
            ROOF_STROKE=RandColorList(cm.roof),
            ROOF_ARCHIVE=RandList([None]),
            WALL=RandColorList(cm.wall),
            # TODO - implement probabilities into RandList, combine windows into one object
            WINDOW=RandList([(72,87,108),(73,65,75),(147,162,182),(170,197,233)]),
            LIGHT_WINDOW=RandColorList([(255,253,168)]),
            DARK_WINDOW=RandColorList([(48,25,52)]),
            WINDOWSILL=RandColorList(cm.roof),
            )
        self.neighborhood = neighborhood
        for arr in [self.ranges,self.colors]:
            for key, value in arr.items():
                if random.random() > self.neighborhood.MONO_THRESHOLD:
                    value.freeze()
                    print("MONO",key)
        self.prev = None
    def makeHouses(self):
        for i in range(self.neighborhood.HOUSE_COUNT):
            yield self.makeHouse(twin=True if random.random() >= self.neighborhood.TWIN_THRESHOLD else False)
    def addWindows(self,wall,data,colors,borderless=True,protruding_roof=None):
        # TODO: adjust window height when roof overlaps bottom of windows
        window_count = int((wall.width-2*data.WINDOW_MARGIN)/(data.WINDOW_WIDTH+data.WINDOW_MARGIN))
        window_height = data.WINDOW_HEIGHT
        wall_height = wall.height
        ## ALT EFFECT: borderless #1
        if borderless:
            vertical = True if 'left' in data.WINDOW_BORDERS else False
            if data.WINDOW_MARGIN == 0 and wall.width > (window_count*data.WINDOW_WIDTH):
                if window_count % 2 == 0:
                    window_count -= data.WINDOW_DELTA
                expand = window_count >> 1
                extra = wall.width-(window_count*data.WINDOW_WIDTH)
            else:
                expand = window_count-1
                extra = 0
        windows = []
        borders = data.WINDOW_BORDERS.copy()
        for j in range(window_count):
            fill = cm.tupwoggle(colors.LIGHT_WINDOW,10) if random.random()>self.neighborhood.WINDOW_LIGHT_PCT else colors.WINDOW
            
            #ALT EFFECT borderless #2
            if borderless:
                if vertical and data.WINDOW_MARGIN == 0:
                    if j > 0:
                        borders.discard('left')
                if data.WINDOW_MARGIN == 0 and j == expand:
                    window = Window(w=data.WINDOW_WIDTH+extra,h=window_height,stroke=colors.WINDOWSILL,borders=borders,fill=fill)
                else:
                    window = Window(w=data.WINDOW_WIDTH,h=window_height,stroke=colors.WINDOWSILL,borders=borders,fill=fill)
            else:
                window = Window(w=data.WINDOW_WIDTH,h=window_height,stroke=colors.WINDOWSILL,borders=borders,fill=fill)
            windows.append((window,data.WINDOW_MARGIN if j>0 else 0,0))
        if len(windows)>0:
            c_windows = Canvas.fromStack(windows,vertical=False)
            floor = Canvas.fromSprites([(wall,0,0),(c_windows,int((wall.width-c_windows.width)/2),int((wall.height-wall_height)/2+(wall.height-c_windows.height)/2))])
        else:
            floor = wall
        return floor
    def makeHouse(self,twin=False):
        # ALT EFFECTS - not sure if these will make it into production code
        terrace = True
        borderless = True
        wallstroke = True

        # TODO - resolve minor conflict between borderless and wallstroke.
        # see - wallstroke = vertical and full-width window overrules wall stroke.
        
        if twin and self.prev:
            data,colors = self.prev
        else:
            data = SimpleNamespace(**{key:value.rand() for key,value in self.ranges.items()})
            colors = SimpleNamespace(**{key:value.rand() for key,value in self.colors.items()})
            ## Secondary fields
            data.WALL_BORDERS = Rect.defineSills(data.WALL_BORDERS if data.WALL_HAS_BORDERS else None)
            data.WINDOW_BORDERS = Window.defineSills(data.WINDOW_BORDERS if data.WINDOW_HAS_BORDERS else None)
            data.WINDOW_HEIGHT = int(data.FLOOR_HEIGHT*data.WINDOW_FLOOR_RATIO)
            data.ROOF_AWNING = data.ROOF_AWNING if data.ROOF_TYPE.HAS_AWNINGS else 0
            data.ROOF_WIDTH = data.FLOOR_WIDTH+data.ROOF_AWNING
            data.ROOF_HEIGHT = int(data.ROOF_WIDTH*data.ROOF_PITCH)
            
            colors.ROOF_STROKE = colors.ROOF_STROKE if data.ROOF_HAS_SURFACE else colors.ROOF
            colors.WALL_STROKE = cm.tupwoggle(colors.WALL,45)

            ## Static fields
            data.ALLEY_WIDTH = 5
            
        ## Create sprites
        roof = data.ROOF_TYPE(
            data.ROOF_WIDTH,
            data.ROOF_HEIGHT,
            fill=colors.ROOF,
            stroke=colors.ROOF_STROKE,
            colors=colors.ROOF_ARCHIVE,
            levels=data.ROOF_LEVELS,
            steplength=data.ROOF_STEP_LENGTH,
            direction=data.ROOF_DIRECTION
            )
        if roof.HAS_COLOR_ARCHIVE:
            colors.ROOF_ARCHIVE = roof.COLOR_ARCHIVE

        ## ALT EFFECT: terrace - works well with short roofs
        if terrace:
            if data.FLOOR_COUNT < 3 and data.ROOF_TYPE in [FpRoof,FlatRoof,StaggeredRoof] and roof.height < data.FLOOR_HEIGHT:
                roof_bg = Rect(w=int(3*data.FLOOR_WIDTH/4),h=data.FLOOR_HEIGHT,fill=colors.WALL)
                roof_bg = self.addWindows(roof_bg,data,colors,borderless=borderless,protruding_roof=roof)
                if roof.width > roof_bg.width:
                    roof = Canvas.fromSprites([(roof_bg,int((roof.width-roof_bg.width)/2),0),(roof,0,0)])
                else:
                    roof = Canvas.fromSprites([(roof_bg,0,0),(roof,0,0)])
                roof2 = data.ROOF_TYPE(
                    roof_bg.width+data.ROOF_AWNING,
                    data.ROOF_HEIGHT,
                    fill=colors.ROOF,
                    stroke=colors.ROOF_STROKE,
                    colors=colors.ROOF_ARCHIVE,
                    levels=data.ROOF_LEVELS,
                    steplength=data.ROOF_STEP_LENGTH,
                    direction=data.ROOF_DIRECTION
                    )
                roof = Canvas.fromStack([roof,roof2])

        

        floors = []
        for i in range(data.FLOOR_COUNT):
            wall = Rect(w=data.FLOOR_WIDTH,h=data.FLOOR_HEIGHT,fill=colors.WALL)
            
            # ALT - add stroke to walls - different border patterns are interesting
            if wallstroke:
                borders = data.WALL_BORDERS.difference({'top'}) if i+1 == data.FLOOR_COUNT else data.WALL_BORDERS
                wall = Rect(w=data.FLOOR_WIDTH,h=data.FLOOR_HEIGHT,fill=colors.WALL,stroke=colors.WALL_STROKE,borders=borders)
            floors.append(self.addWindows(wall,data,colors,borderless=borderless))
        c_floors = Canvas.fromStack(floors)
        c = Canvas.fromStack([c_floors,roof])
        self.prev = (data,colors)
        return c, data.ALLEY_WIDTH, 0
