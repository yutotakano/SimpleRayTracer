from PIL import Image
import math
from numpy import array

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y, self.z + v.z)
    
    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z)

    def __truediv__(self, c):
        return Vector(self.x * c, self.y / c, self.z / c)
    
    def __mul__(self, c):
        return Vector(self.x * c, self.y * c, self.z * c)
    
    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'

def dot(v, w):
    return v.x*w.x + v.y*w.y + v.z*w.z

def cross(v, w):
    return Vector(v.y*w.z - v.z*w.y, v.z*w.x - v.x*w.z, v.x*w.y - v.y*w.x)

def modulo(v):
    return math.sqrt(v.x**2 + v.y**2 + v.z**2)

def unit(v):
    return v / modulo(v)

def containing_plane(v, w):
    normal = cross(v, w)
    d = dot(normal, v)
    return Plane(normal, d)

v_o = Vector(0, 0, 0)

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

class Box:
    def __init__(self, p1, width, height, depth):
        self.p1 = p1
        self.w = width
        self.h = height
        self.d = depth
    
    def intersect(self, ray):
        # create planes for all 6 sides
        # check if ray and plane have a solution
        # if ANY plane has a solution return true, together with value for ray distance, and plane normal

        n1 = Vector(0, 0, 1)
        p1 = Plane(n1, dot(n1, self.p1))
        p2 = Plane(n1, dot(n1, self.p1 + Vector(0, 0, self.d)))

        n2 = Vector(0, 1, 0)
        p3 = Plane(n2, dot(n2, self.p1))
        p4 = Plane(n2, dot(n2, self.p1 + Vector(0, self.h, 0)))
        
        n3 = Vector(1, 0, 0)
        p5 = Plane(n3, dot(n3, self.p1))
        p6 = Plane(n3, dot(n3, self.p1 + Vector(self.w, 0, 0)))

        trues = []
        for plane in [p1, p2, p3, p4, p5, p6]:
            p_intersection = plane.intersect(ray)
            if isinstance(p_intersection[1], Vector):
                # print(p_intersection[1], plane.normal)
                # single intersection
                if (
                    p_intersection[1].x >= self.p1.x and p_intersection[1].x <= self.p1.x+self.w and
                    p_intersection[1].y >= self.p1.y and p_intersection[1].y <= self.p1.y+self.h and
                    p_intersection[1].z >= self.p1.z and p_intersection[1].z <= self.p1.z+self.d
                ):
                    trues.append((True, p_intersection[0], plane.normal))
            # discard when intersection is a line, since you basically can't see it
        if len(trues) > 0:
            return min(trues, key=(lambda a: a[1]))
        return None

        

class Plane:
    def __init__(self, n, d):
        self.normal = unit(n)
        self.d = d
    def __repr__(self):
        return 'Normal: ' + str(self.normal) + ', d: ' + str(self.d)
    
    def intersect(self, ray):
        if dot(ray.direction, self.normal) == 0:
            return (0, ray)

        t = (dot(ray.origin, self.normal) - self.d) / (dot(ray.direction, self.normal)*(-1))
        return (t, ray.origin + ray.direction*t)

class World:
    def __init__(self):
        self.things = []
    
    def add(self, thing):
        self.things.append(thing)

class Screen:
    def __init__(self, w, h, focal_length):
        self.width = w
        self.height = h
        self.focal = Vector(0, 0, focal_length*(-1))
    
    def render(self, world, w, h):
        jitter = [
            -1.0/4.0,  3.0/4.0,
             3.0/4.0,  1.0/3.0,
            -3.0/4.0, -1.0/4.0,
             1.0/4.0, -3.0/4.0,
        ]
        pixels = []
        for i in range(h):
            pixels.append([])
            for j in range(w):
                # find ray from focal to pixel
                # intersect all objects with ray
                # get closest (i.e. shortest ray value
                # get surface normal
                # find angle from surface normal to ray
                # transform to lightness
                # assign pixel value 1-255 on output
                value = 0
                # take 4 samples, average
                for sample in range(3):
                    # ray from focal to pixel
                    ray = Ray(self.focal, Vector(((j + jitter[2*sample]) - (w / 2))*self.width/w, ((i+ jitter[2*sample+1]) - (h / 2))*self.height/h, 0) - self.focal)
                    if modulo(ray.direction) == v_o:
                        value += 255
                        continue
                    # intersections is a list with [None, (True, 3.2, Vector), etc]
                    # maybe add + [(True, 300, Vector(0,0,-1))]
                    intersections = [thing.intersect(ray) for thing in world.things]
                    intersections = [intersection for intersection in intersections if intersection]
                    # get closest
                    if len(intersections) == 0:
                        continue
                    closest_intersection = min(intersections, key=(lambda item: item[1]))
                    value += (255 - (80*math.acos((dot(closest_intersection[2],ray.direction)) / (modulo(closest_intersection[2])*modulo(ray.direction)))))

                pixels[i].append(value/4.0)
        return pixels


world = World()
world.add(Box(Vector(0, -120, 40), 100, 100, 100))
world.add(Box(Vector(-100, -20, 50), 50, 50, 50))
world.add(Box(Vector(20, 30, 40), 30, 30, 30))

screen = Screen(100, 100, 25)

Image.fromarray(array(screen.render(world, 500, 500))).show()