from collections import namedtuple
import math
from PIL import Image
import random

from .colors import cm
from .renderers import *
from .utils import Point, Padding

class Sprite(object):
    def __init__(self,default_color=(0,0,0,0),woggle=True,max_shift=None,woggle_default=True):
        self.printer = Bresenham()
        self.default_color = default_color
        self.woggle = woggle
        self.max_shift = max_shift
        self.woggle_default = woggle_default
    def generateCanvas(self,width,height):
        self.width = width
        self.height = height
        self.data = [None]*self.width*self.height
    def query(self,x,y):
        if 0 <= x < self.width and 0<= y < self.height:
            return self.data[self.width*y + x]            
    def plot(self,x,y,stroke=(0,0,0)):
        if 0 <= x < self.width and 0<= y < self.height:
            self.data[self.width*y + x] = stroke
    def getPx(self):
        if self.woggle:
            if self.max_shift is None:
                return [cm.tupwoggle(item) if item else None for item in self.data]
            return [cm.tupwoggle(item,self.max_shift) if item else None for item in self.data]
        return self.data
    def export(self,file=None,scale=5):
        scale = math.ceil(1500/self.width)
        im = Image.new('RGBA',(self.width,self.height))
        data_ = []
        """for y in range(self.height):
            if self.woggle_default:
                data_.extend([cm.tupwoggle(self.default_color,max_shift=3) if not color else cm.tupwoggle(color) for color in  self.data[(self.height-y-1)*self.width:(self.height-y)*self.width]])
            else:
                data_.extend([self.default_color if not color else cm.tupwoggle(color) for color in  self.data[(self.height-y-1)*self.width:(self.height-y)*self.width]])"""
        for y in range(self.height):
            if self.woggle_default:
                data_.extend([cm.tupwoggle(self.default_color,max_shift=3) if not color else color for color in  self.data[(self.height-y-1)*self.width:(self.height-y)*self.width]])
            else:
                data_.extend([self.default_color if not color else color for color in  self.data[(self.height-y-1)*self.width:(self.height-y)*self.width]])
        im.putdata(data_)
        im = im.resize((self.width*scale,self.height*scale))
        if file:
            im.save(file)
        return im
    # make self into a copy of another sprite
    def copy(self,sprite):
        self.generateCanvas(sprite.width,sprite.height)
        self.data = sprite.data
"""class Rect(Sprite):
    def __init__(self,w,h,fill=None,stroke=None,**kwargs):
        Sprite.__init__(self,**kwargs)
        self.generateCanvas(w,h)
        if fill:
            for x in range(w):
                for y in range(h):
                    self.plot(x,y,fill)
        if stroke:
            for x,y in self.printer.lines((0,0),(0,h-1),(w-1,h-1),(w-1,0),closed=True):
                self.plot(x,y,stroke)"""

class RectGradient(Sprite):
    def __init__(self,w,h,color0,color1,vertical=True,**kwargs):
        Sprite.__init__(self,**kwargs)
        self.generateCanvas(w,h)
        delta = tuple(item/h for item in self.subtractTuples(color1,color0))
        for y in range(h):
            color = tuple(int(color0[i]+y*delta[i]) for i in range(len(color0)))
            for x in range(w):
                self.plot(x,y,color)
        
    def addTuples(self,tup0,tup1):
        return tuple(tup0[i]+tup1[i] for i in range(len(tup0)))
    def subtractTuples(self,tup0,tup1):
        return tuple(tup0[i]-tup1[i] for i in range(len(tup0)))
        
# TODO - allow different max_shift values for window fill; window frame
class Rect(Sprite):
    def __init__(self,w,h,fill=None,stroke=None,borders=None,curtains=False,**kwargs):
        #Rect.__init__(self,w,h,fill,max_shift=max_shift)
        #def __init__(self,w,h,fill=None,stroke=None,**kwargs):
        Sprite.__init__(self,**kwargs)
        self.generateCanvas(w,h)
        if fill:
            for x in range(w):
                for y in range(h):
                    self.plot(x,y,fill)                
        if not type(borders) is set:
            borders = self.defineSills(borders)
        self.borderPixels = set()
        self.addSill(borders,stroke)
    @staticmethod
    def defineSills(key):
        if key in ['left','right','top','bottom']:
            return {key}
        elif type(key) is str and key[0] == '-':
            return {'left','right','top','bottom'}.difference({key[1:]})
        elif key == 'all':
            return {'left','right','top','bottom'}
        elif key == 'vertical':
            return {'left','right'}
        elif key == 'horizontal':
            return {'top','bottom'}
        else:
            return set()
    def addSill(self,borders,stroke,overwrite=True):
        if 'left' in borders or 'vertical' in borders:
            for y in range(self.height):
                self._plot(0,y,stroke,overwrite)
        if 'right' in borders or 'vertical' in borders:
            for y in range(self.height):
                self._plot(self.width-1,y,stroke,overwrite)
        if 'bottom' in borders or 'horizontal' in borders:
            for x in range(self.width):
                self._plot(x,0,stroke,overwrite)
        if 'top' in borders or 'horizontal' in borders:
            for x in range(self.width):
                self._plot(x,self.height-1,stroke,overwrite)
    def _plot(self,x,y,stroke,overwrite):
        if not overwrite and (x,y) in self.borderPixels:
            return
        self.plot(x,y,stroke)
        self.borderPixels.add((x,y))
class Window(Rect):
    def __init__(self,*args,**kwargs):
        Rect.__init__(self,*args,max_shift=3,**kwargs)
class RoofMeta:
    HAS_AWNINGS = True
    HAS_COLOR_ARCHIVE = False
    def fillBetween(self,fill):
        for y in range(self.height):
            previous = None
            border = 0
            plot_ = []
            for x in range(self.width):
                current = self.query(x,y)
                #if current == stroke and not previous:
                if current is not None and not previous:
                    border += 1
                previous = current
                if border % 2 and not current:
                    plot_.append((x,y))
            if not border % 2:
                for x,y in plot_:
                    self.plot(x,y,fill)

# Doesn't work great with contrasting fill-stroke
class FpRoof(Sprite,RoofMeta):
    def __init__(self,w,h,fill=None,stroke=None,**kwargs):
        Sprite.__init__(self)
        h = math.ceil(w/13)
        w1 = w >> 3
        bx = 1+(w-w1)>>1
        cx = (w-1)-((w-w1)>>1)
        a = Point(0,0)
        b = Point(bx,h-2)
        b1 = Point(bx,h-1)
        c = Point(cx,h-2)
        c1 = Point(cx,h-1)
        d = Point(w-1,0)
        self.generateCanvas(w,h)
        for p0,p1 in [(a,b),(d,c),(b1,c1)]:
            for x, y in self.printer.line(*p0,*p1):
                self.plot(x,y,stroke)
        if fill:
            self.fillBetween(fill)
        
class SimpleRoof(Sprite, RoofMeta):
    def __init__(self,w,h,fill=None,stroke=None,leanto=False,direction=None,**kwargs):
        if not stroke:
            stroke = fill
        Sprite.__init__(self)
        if leanto:
            if direction is None:
                direction = random.choice([True,False])
            h >> 1
            a = Point(0,0)
            c = Point(w-1,0)
            b = Point(0,h-1) if direction else Point(w-1,h-1)
        else:
            a = Point(0,0)
            b = Point(math.ceil(w/2),h-1)
            c = Point(w-1,0)
        self.generateCanvas(w,h)
        for x,y in self.printer.line(*a,*b):
            self.plot(x,y,stroke)
        for x,y in self.printer.line(*c,*b):
            self.plot(x,y,stroke)
        self.plot(*b,stroke)
        if fill:
            for y in range(self.height):
                previous = None
                border = 0
                plot_ = []
                for x in range(self.width):
                    current = self.query(x,y)
                    if current == stroke and not previous:
                        border += 1
                    previous = current
                    if border % 2 and not current:
                        plot_.append((x,y))
                if not border % 2:
                    for x,y in plot_:
                        self.plot(x,y,fill)
class FlatRoof(Rect, RoofMeta):
    def __init__(self,w,h,fill=None,stroke=None,**kwargs):
        Rect.__init__(self,w,1,fill=fill,stroke=stroke)

class LeanToRoof(SimpleRoof, RoofMeta):
    HAS_AWNINGS=False
    def __init__(self,*args,**kwargs):
        SimpleRoof.__init__(self,*args,**kwargs,leanto=True)

class NullRoof(Sprite, RoofMeta):
    HAS_AWNINGS=False
    def __init__(self,*args,**kwargs):
        Sprite.__init__(self)
        self.generateCanvas(0,0)

class StaggeredRoof(Sprite, RoofMeta):
    HAS_COLOR_ARCHIVE = True
    def __init__(self,w,h,fill=None,stroke=None,colors=None,levels=None,steplength=None,max_shift=10,**kwargs):
        Sprite.__init__(self)
        
        """if type(fill) is list:
            self.COLOR_ARCHIVE = fill
        else:
            self.COLOR_ARCHIVE = [cm.tupwoggle(fill,max_shift) for level in range(levels)]"""
        if colors:
            self.COLOR_ARCHIVE = colors
        else:
            self.COLOR_ARCHIVE = [(cm.tupwoggle(fill,max_shift),cm.tupwoggle(stroke,max_shift)) for level in range(levels)]
        ystep = int(h/levels)
        self.generateCanvas(w,h)
        dx = 0
        y = 0
        for level in range(levels):
            dy = 0
            fill,stroke = self.COLOR_ARCHIVE[level]
            while dy < ystep and y+dy < self.height:
                for x in range(dx,self.width-dx):
                    if x in [dx,self.width-dx-1]:
                        color = stroke
                    elif y+dy+1 == ystep*levels:
                        color = stroke
                    elif dy + 1 == ystep and (x - dx <= steplength or self.width-dx-x-1 <= steplength):
                        color = stroke
                    else:
                        color = fill
                    self.plot(x,y+dy,color)
                dy += 1
                dx+= 1
            y += ystep
            dx += steplength
        
        
        
        
                    
            

# combine multiple sprites
class Canvas(Sprite):
    def __init__(self,width=None,height=None,pad=None,**kwargs):
        #padding:
        #1 val = all 4
        #2 vals = top/bottom , left/right
        #3 vals = top, left/right, bottom
        #4 vals = top, right, bottom, left
        self.pad = Padding(0,0,0,0) if not pad else Padding(*pad)
        Sprite.__init__(self,woggle=False,**kwargs)
        self.generateCanvas(width+self.pad.right+self.pad.left,height+self.pad.bottom+self.pad.top)
        #self.plot(2,5,(255,0,0))
    @classmethod
    def fromSprites(cls,sprites,**kwargs):
        # sprites = [(sprite, dx, dy), ...]
        width = max(sprite.width+dx for sprite,dx,dy in sprites)
        height = max(sprite.height+dy for sprite,dx,dy in sprites)
        canvas = cls(width,height,**kwargs)
        for sprite, dx, dy in sprites:
            canvas.plotPoints(sprite,dx,dy)
        return canvas
    # todo - z-index controls for stack
    @classmethod
    def fromStack(cls,sprites,vertical=True,alignment='centered',**kwargs):
        # sprites = [(sprite, dx1, dy1), ...]
        sprites_ = []
        for sprite in sprites:
            
            if type(sprite) is tuple:
                sprites_.append(sprite)
            elif sprite.width > 0 and sprite.height > 0:
                sprites_.append((sprite,0,0))
        sprites = sprites_
        def align(sprite,canvas):
            dim = 'width' if vertical else 'height'
            if alignment in ['left','bottom']:
                return 0
            delta = getattr(canvas,dim) - getattr(sprite,dim)
            if alignment in ['right','top']:
                return delta
            else:
                return int(delta/2)
        if vertical:
            width = max(sprite.width for sprite,dx1,dy1 in sprites)
            height = sum(sprite.height+dy1 for sprite,dx1,dy1 in sprites)
            canvas = cls(width,height,**kwargs)
            dy = 0
            for sprite,dx1,dy1 in sprites:
                dx = align(sprite,canvas)
                canvas.plotPoints(sprite,dx+dx1,dy+dy1)
                dy += sprite.height + dy1
        else:
            width = sum(sprite.width+dx1 for sprite,dx1,dy1 in sprites)
            height = max(sprite.height for sprite,dx1,dy1 in sprites)
            canvas = cls(width,height,**kwargs)
            dx = 0
            for sprite,dx1,dy1 in sprites:
                dy = align(sprite,canvas)
                canvas.plotPoints(sprite,dx+dx1,dy+dy1)
                dx += sprite.width + dx1
        return canvas
    def plotPoints(self,sprite,dx=0,dy=0):
        data = sprite.getPx()
        for y in range(sprite.height):
            for x in range(sprite.width):
                stroke = data[y*sprite.width+x]
                if stroke:
                    self.plot(x+dx+self.pad.left,y+dy+self.pad.bottom,stroke)
