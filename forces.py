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
        if particule.avoir_masse_inverse() == 0:
            return
        particule.ajouter_force(self.gravite * particule.avoir_masse())

class ForceGravitation(ForceGenerale):
    def __init__(self, particules : list[Particule], constante_gravitationelle = 6.67e-1):
        self.particules = particules
        self.constante_graitationelle = constante_gravitationelle
        self.derniere_force = Vecteur3()
    def appliquer(self, particule : Particule, _):
        if particule.avoir_masse_inverse() == 0:
            return
        for p in self.particules:
            if p == particule or p.avoir_masse_inverse() == 0:
                continue
            u = particule.position - p.position
            d2 = (u.norme() - p.rayon - particule.rayon)**2
            if d2 <= 0:
                continue
            Fg = u.normaliser() * (self.constante_graitationelle * (particule.avoir_masse() * p.avoir_masse()) / d2) * 10
            p.ajouter_force(Fg)
            self.derniere_force = Fg
    def afficher(self, particule : Particule, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        afficher_ligne(particule.position,particule.position+self.derniere_force*-20,fenetre,camera_rotation,camera_translation,(0,0,255),10)

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
    def __init__(self, profondeur_max : float, hauteur_liquide : float, densite_liquide = 1000.0):
        self.profondeur_max = profondeur_max
        self.hauteur_liquide, self.densite_liquide = hauteur_liquide, densite_liquide
    def appliquer(self, particule : Particule, _):
        profondeur = particule.position.y
        if profondeur >= self.hauteur_liquide:
            return
        force = Vecteur3()
        volume = (4 * math.pi * particule.rayon**3)/3
        if profondeur <= self.hauteur_liquide - self.profondeur_max:
            force.y = self.densite_liquide * volume
        else:
            force.y = self.densite_liquide * volume * (self.hauteur_liquide - profondeur) / (2 * self.profondeur_max)
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

class ForceBungee(ForceRessort):
    def appliquer(self, _):
        if (self.a.position - self.b.position).norme() < self.longeur:
            return
        force = self.calculer_force(self.a.position, self.b.position)
        self.a.ajouter_force(force)
        self.b.ajouter_force(-force)

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
    def afficher(self, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        if pg.key.get_pressed()[self.touche]:
            afficher_ligne(self.particule.position,self.particule.position + (self.force(self.particule,0.016) if callable(self.force) else self.force) * -0.02, fenetre, camera_rotation, camera_translation, (180,75,0), 30)

class ForcePropulseurDirige(ForcePropulseur):
    def __init__(self, particule : Particule, direction : Particule, norme = 10, touche = pg.K_0):
        self.direction = direction
        self.norme = norme
        super().__init__(particule,lambda _, __: (self.direction.position - self.particule.position).normaliser() * self.norme, touche)