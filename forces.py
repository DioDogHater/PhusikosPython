from core import *

class Force:
    def appliquer(self, duration : float):
        pass
    def afficher(self, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        pass

class ForceGenerale:
    def appliquer(self, particule : Particule, duration : float):
        pass
    def afficher(self, particule : Particule, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        pass

class ForceGravite(ForceGenerale):
    def __init__(self, acceleration = Vecteur3(0,-9.8,0)):
        self.gravite = acceleration
    def appliquer(self, particule : Particule, _):
        particule.ajouter_force(self.gravite * particule.avoir_masse())

# Air drag
class ForceTrainee(ForceGenerale):
    def __init__(self, k1 : float, k2 : float):
        self.k1, self.k2 = k1, k2
    def appliquer(self, particule : Particule, _):
        force = particule.velocite
        coeff_trainee = force.norme()
        coeff_trainee = coeff_trainee * self.k1 + (coeff_trainee ** 2) * self.k2
        particule.ajouter_force(force * -coeff_trainee)

class ForcePousseeArchimede(ForceGenerale):
    def __init__(self, profondeur_max : float, volume : float, hauteur_liquide : float, densite_liquide = 1000.0):
        self.volume = volume                    # Volume de chaque particule dans la simulation
        self.profondeur_max = profondeur_max
        self.hauteur_liquide, self.densite_liquide = hauteur_liquide, densite_liquide
    def appliquer(self, particule : Particule, _):
        profondeur = particule.position.y
        if profondeur >= self.hauteur_liquide:
            return
        force = Vecteur3()
        if profondeur <= self.hauteur_liquide - self.profondeur_max:
            force.y = self.densite_liquide * self.volume
        else:
            force.y = self.densite_liquide * self.volume * (self.hauteur_liquide - profondeur) / (2 * self.profondeur_max)
        force -= particule.velocite
        particule.ajouter_force(force)

    def afficher(self, particule : Particule, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        if particule.position.y < self.hauteur_liquide:
            surface = particule.position.copier()
            surface.y = self.hauteur_liquide
            surface = appliquer_transformation(surface, camera_rotation, camera_translation)
            pg.draw.circle(fenetre, (128,128,200), surface.projection(fenetre), 64 / surface.z, 1)

class ForceRessort(Force):
    def __init__(self, a : Particule, b : Particule, k = 20, longeur = 0, damping = 0.75):
        self.a, self.b = a, b
        self.k, self.damping = k, damping
        self.longeur = longeur if longeur != 0 else (a.position - b.position).norme()
    def calculer_force(self, a : Vecteur3, b : Vecteur3):
        force = a - b
        norme = (force.norme() - self.longeur) * self.k
        force = force.normaliser() * (-norme * self.damping)
        return force
    def appliquer(self, _):
        force = self.calculer_force(self.a.position, self.b.position)
        self.a.ajouter_force(force)
        self.b.ajouter_force(-force)
    def afficher_points(self, a : Vecteur3, b : Vecteur3, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        dist = abs((a - b).norme() - self.longeur) / self.longeur * 255
        dist = min(dist, 255)
        couleur = (dist,255-dist,0)
        afficher_ligne(a,b,fenetre,camera_rotation,camera_translation,couleur,15)
    def afficher(self, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        self.afficher_points(self.a.position, self.b.position, fenetre, camera_rotation, camera_translation)

class ForceRessortFixe(ForceRessort):
    def __init__(self, fixation : Vecteur3, b : Particule, k = 20, longeur = 0, damping = 0.75):
        self.fixation, self.b = fixation, b
        self.k, self.damping = k, damping
        self.longeur = longeur if longeur != 0 else (fixation - b.position).norme()
    def appliquer(self, _):
        force = self.calculer_force(self.b.position, self.fixation)
        self.b.ajouter_force(force)
    def afficher(self, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        self.afficher_points(self.fixation, self.b.position, fenetre, camera_rotation, camera_translation)

class ForcePropulseur(Force):
    def __init__(self, particule : Particule, force = Vecteur3(0,10,0), touche = pg.K_0):
        self.particule = particule
        self.force = force
        self.touche = touche
    def appliquer(self, duration : float):
        if pg.key.get_pressed()[self.touche]:
            self.particule.ajouter_force(self.force(self.particule, duration) if callable(self.force) else self.force)