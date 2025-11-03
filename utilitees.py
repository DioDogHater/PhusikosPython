from phusikos import *
import pygame as pg

class Cameraman:
    def __init__(self):
        self.position = Vecteur3(0,0,-10)
        self.rotation = Vecteur3(0,0,0)
    # BROKEN
    def suivre(self, position_initiale : Vecteur3, position_finale : Vecteur3, distance : float = 10, vitesse : float = 0.5):
        direction = (position_finale - position_initiale)
        dist = direction.norme() - distance
        direction = direction.normaliser() * dist
        return lerp(position_initiale, direction, vitesse)
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
        self.position += Matrice3x3.rotation_Y(-self.rotation.y) * (Vecteur3(droite - gauche, haut - bas, avant - arriere) * deltaTime * (20.0 if keys[pg.K_LSHIFT] else 10.0))
        return Matrice3x3.rotation_X(self.rotation.x) * Matrice3x3.rotation_Y(self.rotation.y), self.position

def construire_echafaudage(steps : int, substeps : int, hauteur : float, particules : list[Particule], liens : list[Lien], forces : list[Force],
                           type_de_connecteur = Barre, position_initiale = Vecteur3(), rayon_aleatoire = False, angle_de_depart = 0, propulseurs = True, masse = 1):
    # Construire un echafaudage
    # steps = Le nombre de cotés de l'echafaudage
    # substeps = La densite de l'echafaudage verticalement
    nv_particules = []
    angle_step = math.pi / steps * 2
    for i in range(steps):
        angle = i * angle_step + angle_de_depart
        pos = Matrice3x3.rotation_Y(angle) * Vecteur3(0,0,-2) + position_initiale
        for j in range(substeps):
            nv_particules.append(Particule(masse, pos + Vecteur3(0,hauteur/(substeps-1),0) * j, rayon = randf(0.25,0.5) if rayon_aleatoire else 0.25))
    liste_connecteurs = liens
    if type_de_connecteur == ForceRessort:
        liste_connecteurs = forces
    for i in range(steps):
        # Liens solides (Barres)
        for j in range(substeps):
            if j < substeps-1:
                # Liens verticaux
                liste_connecteurs.append(type_de_connecteur(nv_particules[i*substeps+j], nv_particules[i*substeps+j+1]))
                # Liens diagonaux
                liste_connecteurs.append(type_de_connecteur(nv_particules[(i-1)*substeps+j+1], nv_particules[i*substeps+j]))
                liste_connecteurs.append(type_de_connecteur(nv_particules[(i-1)*substeps+j], nv_particules[i*substeps+j+1]))
            # Liens horizontaux
            liste_connecteurs.append(type_de_connecteur(nv_particules[(i-1)*substeps+j], nv_particules[i*substeps+j]))
            # Liens diagonaux entres les "bases" de chaque hauteur
            liste_connecteurs.append(type_de_connecteur(nv_particules[(i-steps//2)*substeps+j], nv_particules[i*substeps+j]))
        # Ajouter un propulseur sur chaque element de la base de la forme
        if propulseurs:
            forces.append(ForcePropulseurDirige(nv_particules[i*substeps],nv_particules[ i*substeps+1],20*substeps,touche=pg.K_1))
            forces.append(ForcePropulseurDirige(nv_particules[i*substeps],nv_particules[ i*substeps+1],-20*substeps,touche=pg.K_2))
            forces.append(ForcePropulseur(nv_particules[i*substeps],
            lambda x,__: (nv_particules[(i-1)*substeps].position - x.position).produit_vectoriel(nv_particules[i*substeps-1].position - x.position).normaliser() * (20*substeps),
            touche=pg.K_3))
            forces.append(ForcePropulseur(nv_particules[ i*substeps],
            lambda x,__: (nv_particules[(i-1)*substeps].position - x.position).produit_vectoriel(nv_particules[i*substeps-1].position - x.position).normaliser() * (-20*substeps),
            touche=pg.K_4))
    particules += nv_particules