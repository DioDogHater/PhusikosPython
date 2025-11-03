from core import *
from contacts import *

class GenerateurDeCollisions:
    def __init__(self, particules : list[Particule]):
        self.particules = particules
    def generer_contacts(self, contacts : list[Contact]):
        pass
    def afficher(self, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        pass

class DetecteurDeCollisions(GenerateurDeCollisions):
    def __init__(self, particules : list[Particule], restitution = 0.25):
        super().__init__(particules)
        self.restitution = restitution
    def collision_sphere_vs_sphere(self, a : Particule, b : Particule):
        normal = a.position - b.position
        dist = normal.norme()
        radii = a.rayon + b.rayon
        if dist < radii:
            penetration = radii - dist
            return Contact(a,b,normal.normaliser(),penetration,self.restitution)
        return None
    def generer_contacts(self, contacts : list[Contact]):
        contacts_existants = {}
        for a in self.particules:
            for b in self.particules:
                if a == b or (a in contacts_existants and b in contacts_existants[a]) or (b in contacts_existants and a in contacts_existants[b]):
                    continue
                contact = self.collision_sphere_vs_sphere(a, b)
                if contact != None:
                    if a in contacts_existants:
                        contacts_existants[a].append(b)
                    else:
                        contacts_existants[a] = [b]
                    contacts.append(contact)

class Sol(GenerateurDeCollisions):
    def __init__(self, particules : list[Particule], hauteur : float, restitution = 0.1):
        super().__init__(particules)
        self.hauteur = hauteur
        self.restitution = restitution
    def generer_contacts(self, contacts : list[Contact]):
        for a in self.particules:
            if a.position.y <= self.hauteur + a.rayon:
                contacts.append(Contact(a,None,Vecteur3(0,1,0),self.hauteur - a.position.y,self.restitution))
    def afficher(self, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        for p in self.particules:
            surface = p.position.copier()
            surface.y = self.hauteur
            afficher_sphere(surface, p.rayon, (75,75,75), fenetre, camera_rotation, camera_translation, False)