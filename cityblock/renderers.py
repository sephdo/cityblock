class Bresenham():
    def vertical(self,x,y0,y1):
        if y0 > y1:
            y1,y0 = y0,y1
        for y in range(y0,y1+1):
            yield x,y
    def horizontal(self,y,x0,x1):
        if x0 > x1:
            x1,x0 = x0,x1
        for x in range(x0,x1+1):
            yield x,y
    # Adapted from https://stackoverflow.com/questions/11678693/all-cases-covered-bresenhams-line-algorithm
    def line(self,x0,y0,x1,y1):
        w = x1-x0
        h = y1-y0

        if not w:
            yield from self.vertical(x0,y0,y1)
            return
        elif not h:
            yield from self.horizontal(y0,x0,x1)
        
        dx0 = -1 if w < 0 else 1 if w > 0 else 0
        dy0 = -1 if h < 0 else 1 if h > 0 else 0
        dx1 = -1 if w < 0 else 1 if w > 0 else 0
        dy1 = 0
        longest = abs(w)
        shortest = abs(h)

        if not longest > shortest:
            longest = abs(h)
            shortest = abs(w)
            dy1 = -1 if h < 0 else 1 if h > 0 else 0
            dx1 = 0
        numerator = longest >> 1
        
        for i in range(longest):
            yield x0,y0
            numerator += shortest
            if not numerator < longest:
                numerator -= longest
                x0 += dx0
                y0 += dy0
            else:
                x0 += dx1
                y0 += dy1
    def lines(self,*points,closed=True):
        points = list(points)
        if closed:
            points.append(points[0])
        for p1,p2 in zip(points[:-1],points[1:]):
            yield from self.line(*p1,*p2)
