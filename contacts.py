from core import *

class Contact:
    def __init__(self, a : Particule, b : Particule | None, normal : Vecteur3, penetration : float, restitution : float):
        self.a, self.b = a, b
        self.penetration = penetration
        self.restitution = restitution
        self.normal = normal
    def resoudre(self, duration : float):
        self.__resoudre_velocite(duration)
        return self.__resoudre_interpenetration(duration)
    # Calculer la vitesse de separation (Vs)
    def calculer_Vs(self):
        velocite_relative = self.a.velocite
        if self.b != None:
            velocite_relative -= self.b.velocite
        return velocite_relative * self.normal
    def recalculer_penetration(self, v : Vecteur3, b : bool = False):
        self.penetration =  (v * self.normal) * (1 if b else -1)
    def __resoudre_velocite(self, duration : float):
        Vs = self.calculer_Vs()
        
        if Vs > 0:
            return
        
        nouvelle_Vs = -Vs * self.restitution

        velocite_par_accel = self.a.acceleration
        if self.b != None:
            velocite_par_accel -= self.b.acceleration
        Vs_par_accel = velocite_par_accel * self.normal * duration

        if Vs_par_accel < 0:
            nouvelle_Vs += self.restitution * Vs_par_accel
            nouvelle_Vs = max(nouvelle_Vs, 0)

        delta_v = nouvelle_Vs - Vs

        masse_inverse_totale = self.a.avoir_masse_inverse()
        if self.b != None:
            masse_inverse_totale += self.b.avoir_masse_inverse()
        
        if masse_inverse_totale <= 0:
            return
        
        impulsion_masse_inverse = self.normal * (delta_v / masse_inverse_totale)

        self.a.velocite += impulsion_masse_inverse * self.a.avoir_masse_inverse()
        if self.b != None:
            self.b.velocite -= impulsion_masse_inverse * self.b.avoir_masse_inverse()
    def __resoudre_interpenetration(self, duration : float):
        if self.penetration <= 0:
            return (Vecteur3(),Vecteur3())
        
        masse_inverse_totale = self.a.avoir_masse_inverse()
        if self.b != None:
            masse_inverse_totale += self.b.avoir_masse_inverse()
        
        if masse_inverse_totale <= 0:
            return (Vecteur3(),Vecteur3())

        mouvement_masse_inverse = self.normal * (self.penetration / masse_inverse_totale)

        mouvements = [mouvement_masse_inverse * self.a.avoir_masse_inverse(), 0]

        self.a.ajouter_impulsion(mouvements[0])
        if self.b != None:
            mouvements[1] = mouvement_masse_inverse * -self.b.avoir_masse_inverse()
            self.b.ajouter_impulsion(mouvements[1])
        return mouvements

class ResolveurDeContacts:
    def __init__(self, nb_iterations = lambda x: 3 * x):
        self.iterations_utilisees = 0
        self.nb_iterations = nb_iterations
    def resoudre_contacts(self, contacts : list[Contact], duration : float):
        self.iterations_utilisees = 0
        max_iterations = self.nb_iterations(len(contacts)) if callable(self.nb_iterations) else self.nb_iterations

        while self.iterations_utilisees < max_iterations:
            Vs_minimum = 0
            index_minimum = None
            for i in range(len(contacts)):
                Vs = contacts[i].calculer_Vs() - contacts[i].penetration
                if Vs < Vs_minimum:
                    Vs_minimum = Vs
                    index_minimum = i
            if index_minimum == None:
                break
            mouvements = contacts[index_minimum].resoudre(duration)
            for i in range(len(contacts)):
                if contacts[i].b != None:
                    if contacts[i].b == contacts[index_minimum].a:
                        contacts[i].recalculer_penetration(mouvements[0],True)
                    if contacts[i].b == contacts[index_minimum].b:
                        contacts[i].recalculer_penetration(mouvements[1],True)
                if contacts[i].a == contacts[index_minimum].a:
                    contacts[i].recalculer_penetration(mouvements[0],False)
                if contacts[i].a == contacts[index_minimum].b:
                    contacts[i].recalculer_penetration(mouvements[1],False)
                
            self.iterations_utilisees += 1

class Lien:
    def __init__(self, a : Particule, b : Particule):
        self.a, self.b = a, b
    def calculer_longeur(self):
        return (self.a.position - self.b.position).norme()
    def generer_contacts(self, contacts : list[Contact]):
        pass
    def afficher(self, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3, couleur : tuple[int] = (255,255,255)):
        afficher_ligne(self.a.position, self.b.position, fenetre, camera_rotation, camera_translation, couleur, 10)

class Cable(Lien):
    def __init__(self, a : Particule, b : Particule, longeur_max : float = 0, restitution = 0.1):
        super().__init__(a,b)
        self.longeur_max = longeur_max if longeur_max != 0 else self.calculer_longeur()
        self.restitution = restitution
    def generer_contacts(self, contacts : list[Contact]):
        longeur = self.calculer_longeur()
        if longeur <= self.longeur_max:
            return
        normal = (self.b.position - self.a.position).normaliser()
        contacts.append(Contact(self.a,self.b,normal,(longeur - self.longeur_max),self.restitution))
    def afficher(self, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        super().afficher(fenetre,camera_rotation,camera_translation,(201,151,14))

class Barre(Lien):
    def __init__(self, a : Particule, b : Particule, longeur : float = 0):
        super().__init__(a,b)
        self.longeur = longeur if longeur != 0 else self.calculer_longeur()
    def generer_contacts(self, contacts : list[Contact]):
        longeur = self.calculer_longeur()
        if math.isclose(longeur, self.longeur):
            return
        normal = (self.b.position - self.a.position).normaliser()
        if longeur > self.longeur:
            contacts.append(Contact(self.a,self.b,normal,abs(self.longeur-longeur)*1,0))
        else:
            contacts.append(Contact(self.a,self.b,-normal,abs(longeur-self.longeur),0))
    def afficher(self, fenetre : pg.Surface, camera_rotation : Matrice3x3, camera_translation : Vecteur3):
        super().afficher(fenetre,camera_rotation,camera_translation,(145, 145, 145))

class BarreMalleable(Lien):
    def __init__(self, a : Particule, b : Particule, longeur : float = 0):
        super().__init__(a,b)
        self.longeur = longeur if longeur != 0 else self.calculer_longeur()
    def generer_contacts(self, contacts : list[Contact]):
        longeur = self.calculer_longeur()
        if math.isclose(longeur, self.longeur):
            return
        normal = (self.b.position - self.a.position).normaliser()
        if longeur > self.longeur:
            contacts.append(Contact(self.a,self.b,normal,-1,0))
        else:
            contacts.append(Contact(self.a,self.b,-normal,-1,0))

# Un lien qui ne permet pas un objet de bouger relativement à sa base
class Soudure(Lien):
    def __init__(self, a : Particule, b : Particule, decalage : Vecteur3 | None = None):
        super().__init__(a,b)
        if decalage == None:
            self.decalage = b.position - a.position
        else:
            self.decalage = decalage
    def generer_contacts(self, contacts : list[Contact]):
        normal = self.decalage - (self.b.position - self.a.position)
        penetration = normal.norme()
        if penetration <= 0.00001:
            return
        contacts.append(Contact(self.b,self.a,normal.normaliser(),penetration * 10,0))