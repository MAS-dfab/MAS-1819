import math

class Shell(object):
    """
    creates a shell of thickness d
    side factor s:
        1 > inside
        0.5 > half half
        0 > outside
    """
    
    def __init__(self, obj, d=1, s=0):
        self.o = obj
        self.d = d
        self.s = s
        
    def get_distance(self,x,y,z):
        do = self.o.get_distance(x,y,z)
        # half half
        #return abs(do)-self.d/2.0
        return abs(do + (self.s-0.5)*self.d)-self.d/2.0
    
class Twist(object):
    def __init__(self,obj=None, ang=0):
        self.o = obj
        self.angle = float(ang)
        
    def get_distance(self,x,y,z):
        bnds = self.o.get_bounds()
        t = (z-bnds[2])/(bnds[5]-bnds[2]) - 0.5
        #theta = (1-t)*self.angle + t*-self.angle
        theta = t*self.angle
        nx = (x*math.cos(theta) - y*math.sin(theta))
        ny = (x*math.sin(theta) + y*math.cos(theta))
        return self.o.get_distance(nx,ny,z)
    
class Taper(object):
    def __init__(self,obj=None, amount=0):
        self.o = obj
        self.amt = float(amount)
        
    def get_distance(self,x,y,z):
        bnds = self.o.get_bounds()
        t = (z-bnds[2])/(bnds[5]-bnds[2])
        #t = z/100.0
        #theta = (1-t)*self.angle + t*-self.angle
        t = min(1,max(0,t))
        off = t*self.amt
        return self.o.get_distance(x,y,z)-off
    
class Transform(object):
    """
    this is the transformation matrix class
    """
    def __init__(self, obj=None):
        self.o = obj
        self.m = PMatrix3D()
        self.sv = PVector()
        self.tv = PVector()
        
    def get_distance(self,x,y,z):
        self.sv.set(x,y,z)
        mc = self.m.get()
        mc.invert()
        mc.mult(self.sv,self.tv)
        return self.o.get_distance(self.tv.x,self.tv.y,self.tv.z)

class Gradient(object):
    """
    modifies obj a with a fraction (f) of obj b
    """
    def __init__(self, obja, objb, f=0.1):
        self.a = obja
        self.b = objb
        self.f = f
        
    def get_distance(self,x,y,z):
        da = self.a.get_distance(x,y,z)
        db = self.b.get_distance(x,y,z)
        return da+self.f*db
