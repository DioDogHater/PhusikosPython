from phusikos import *
import pygame as pg

class Cameraman:
    def __init__(self):
        self.position = Vecteur3(0,0,-10)
        self.rotation = Vecteur3(0,0,0)
    # BROKEN
    def suivre(self, position_initiale : Vecteur3, position_finale : Vecteur3, distance : float = 10, vitesse : float = 0.5):
        direction = (position_finale - position_initiale)
        dist = direction.norme() - 1
        direction = direction.normaliser() * dist
        return lerp(position_initiale, direction, 0.5)
    def freecam(self, deltaTime : float):
        keys = pg.key.get_pressed()
        avant = keys[pg.K_w]
        arriere = keys[pg.K_s]
        gauche = keys[pg.K_a]
        droite = keys[pg.K_d]
        haut = keys[pg.K_e]
        bas = keys[pg.K_q]
        rel = pg.mouse.get_rel()
        self.rotation.x -= rel[1] * 0.0025
        self.rotation.y -= rel[0] * 0.0025
        self.rotation.x = min(max(self.rotation.x, math.radians(-90)), math.radians(90))
        self.position += Matrice3x3.rotation_Y(-self.rotation.y) * (Vecteur3(droite - gauche, haut - bas, avant - arriere) * deltaTime * 5)
        return Matrice3x3.rotation_X(self.rotation.x) * Matrice3x3.rotation_Y(self.rotation.y), self.position