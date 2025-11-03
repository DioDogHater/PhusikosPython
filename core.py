import math
import pygame as pg
import random

def randf(minimum : float, maximum : float):
    return random.random() * (maximum - minimum) + minimum

def lerp(a, b, t : float):
    return a + (b - a) * t

def aspect_ratio(fenetre : pg.Surface):
    return fenetre.get_width() / fenetre.get_height()

# Vecteur en trois dimensions (3 composantes, soit x, y, z)
class Vecteur3:
    def __init__(self,x=0,y=0,z=0):
        self.x, self.y, self.z = (x,y,z)

    def produit_scalaire(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def produit_vectoriel(self, other):
        return Vecteur3(self.y * other.z - self.z * other.y,
                        self.z * other.x - self.x * other.z,
                        self.x * other.y - self.y * other.x)
    
    def norme_carree(self):
        return self.produit_scalaire(self)
    
    def norme(self):
        return math.sqrt(self.norme_carree())
    
    def normaliser(self):
        m = self.norme()
        if m == 0:
            return Vecteur3()
        return self / m
    
    def copier(self):
        return Vecteur3(self.x, self.y, self.z)
    
    def zclip(self, b, z = 0.1):
        # self = (x0, y0, z0)
        # b    = (x1, y1, z1)
        # x = x0 + (x1 - x0) * t
        # y = y0 + (y1 - y0) * t
        # z = z0 + (z1 - z0) * t
        # (z - z0) / (z1 - z0) = t
        if b.z - self.z == 0:
            return self
        t = (z - self.z) / (b.z - self.z)
        return lerp(self, b, t)

    def projection(self, fenetre : pg.Surface):
        if self.z > 0:
            return ((self.x / (self.z * 0.5) + 1) * 0.5 * fenetre.get_width() / aspect_ratio(fenetre), (-self.y / (self.z * 0.5) + 1) * 0.5 * fenetre.get_height())
        else:
            return (0,0)
    
    def __neg__(self):
        return Vecteur3(-self.x,-self.y,-self.z)
    def __add__(self, other):
        return Vecteur3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other):
        return Vecteur3(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, other):
        if type(other) == Vecteur3:
            return self.produit_scalaire(other)
        else:
            return Vecteur3(self.x * other, self.y * other, self.z * other)
    def __truediv__(self, other):
        return Vecteur3(self.x / other, self.y / other, self.z / other)
    def __pow__(self, other):
        return Vecteur3(self.x ** other, self.y ** other, self.z ** other)
    def __mod__(self, other):
        return self.produit_vectoriel(other)
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            raise IndexError("Index out of range")
    def __str__(self):
        return f"<{self.x}, {self.y}, {self.z}>"
    def __repr__(self):
        return self.__str__()

class Matrice3x3:
    def __init__(self,arg):
        if type(arg) == list:
            self.elements = arg
        else:
            self.elements = [[arg(i,j) if callable(arg) else arg for j in range(3)] for i in range(3)]
    @classmethod
    def identite(self):
        return Matrice3x3(lambda i,j: int(i == j))
    @classmethod
    def scale(self, scale = [1,1,1]):
        return Matrice3x3(lambda i,j: scale[i] if (i == j) else 0)
    @classmethod
    def rotation_X(self, angle : float):
        cos, sin = math.cos(angle), math.sin(angle)
        return Matrice3x3([[1,    0,    0],
                           [0,  cos, -sin],
                           [0,  sin,  cos]])
    @classmethod
    def rotation_Y(self, angle : float):
        cos, sin = math.cos(angle), math.sin(angle)
        return Matrice3x3([[cos,  0,  sin],
                           [0,    1,    0],
                           [-sin, 0,  cos]])
    @classmethod
    def rotation_Z(self, angle : float):
        cos, sin = math.cos(angle), math.sin(angle)
        return Matrice3x3([[cos, -sin,  0],
                           [sin,  cos,  0],
                           [0,     0,   1]])
    @classmethod
    def rotation_XYZ(self, angles : Vecteur3):
        return self.rotation_X(angles.x) * self.rotation_Y(angles.y) * self.rotation_Z(angles.z)
    @classmethod
    def rotation_ZYX(self, angles : Vecteur3):
        return self.rotation_Z(angles.z) * self.rotation_Y(angles.y) * self.rotation_X(angles.x)
    def copier(self):
        return Matrice3x3(self.elements)
    def __getitem__(self, index):
        return self.elements[index]
    def __add__(self, other):
        return Matrice3x3(lambda i,j: self[i][j] + other[i][j])
    def __sub__(self, other):
        return Matrice3x3(lambda i,j: self[i][j] - other[i][j])
    def __mul__(self, other):
        if type(other) == Matrice3x3:
            return Matrice3x3(lambda i,j: sum([self[i][k] * other[k][j] for k in range(3)]))
        elif type(other) == Vecteur3:
            return Vecteur3(sum([self[0][j] * other[j] for j in range(3)]),
                            sum([self[1][j] * other[j] for j in range(3)]),
                            sum([self[2][j] * other[j] for j in range(3)]))
        else:
            return Matrice3x3(lambda i,j: self[i][j] * other)

def appliquer_transformation(v : Vecteur3, M : Matrice3x3, translation : Vecteur3) -> Vecteur3:
    return M * (v + translation)

def afficher_ligne(a : Vecteur3, b : Vecteur3, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3, couleur : tuple[int], epaisseur : int):
    point_a = appliquer_transformation(a,camera_rotation,camera_translation)
    point_b = appliquer_transformation(b,camera_rotation,camera_translation)
    if point_a.z > 0 or point_b.z > 0:
        if point_a.z <= 0:
            point_a = point_a.zclip(point_b)
        elif point_b.z <= 0:
            point_b = point_b.zclip(point_a)
        pg.draw.line(fenetre,couleur,point_a.projection(fenetre),point_b.projection(fenetre),max(math.ceil(epaisseur/max(point_a.z,point_b.z,1)),0))

def afficher_sphere(position : Vecteur3, rayon : float, couleur : tuple, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3, outline = True):
        new_pos = appliquer_transformation(position, camera_rotation, camera_translation)
        if new_pos.z > 0:
            pos = new_pos.projection(fenetre)
            ar = aspect_ratio(fenetre)
            pg.draw.circle(fenetre, couleur, pos, fenetre.get_width()*rayon/ar/new_pos.z)
            if outline:
                pg.draw.circle(fenetre, (0,0,0), pos, fenetre.get_width()*rayon/ar/new_pos.z, 2)

class Particule:
    def __init__(self, masse : float, position : Vecteur3, velocite = Vecteur3(), acceleration = Vecteur3(), rayon = 0.25, damping = 0.85):
        self.position = position
        self.velocite = velocite
        self.acceleration = acceleration
        self.damping = damping
        self.rayon = rayon
        if masse != 0:
            self.__masse_inverse = 1 / masse
        else:
            self.__masse_inverse = 0
        self.__accum_forces = Vecteur3()
    
    def integrer(self, duration : float):
        if duration <= 0:
            return
        
        self.position += self.velocite * duration

        acceleration_resultante = self.acceleration + self.__accum_forces * self.avoir_masse_inverse()
        self.velocite += acceleration_resultante * duration

        self.velocite *= math.pow(self.damping, duration)

        self.__accum_forces = Vecteur3()
    
    def ajouter_force(self, force : Vecteur3):
        self.__accum_forces += force
    
    def ajouter_impulsion(self, impulsion : Vecteur3):
        self.velocite += impulsion

    def avoir_masse(self):
        if self.__masse_inverse != 0:
            return 1 / self.__masse_inverse
        else:
            return math.inf
    
    def avoir_masse_inverse(self):
        return self.__masse_inverse
    
    def changer_masse(self, nv_masse : float):
        if nv_masse != 0:
            self.__masse_inverse = 1 / nv_masse
        else:
            self.__masse_inverse = 0
    
    def afficher_point(self, couleur : tuple, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        afficher_sphere(self.position, self.rayon, couleur, fenetre, camera_rotation, camera_translation)