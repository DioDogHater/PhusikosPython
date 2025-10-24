import pygame as pg
import random as rand
from phusikos import *
import utilitees as utils

FPS = 60

pg.init()
fenetre = pg.display.set_mode((500, 500), pg.RESIZABLE)
clock = pg.time.Clock()

cameraman = utils.Cameraman()

if __name__ == "__main__":
    forces_generales : list[ForceGenerale] = []
    forces_generales.append(ForceGravite())

    # Trainee aerienne (friction de l'air)
    #forces_generales.append(ForceTrainee(0.05, 0.001))

    # Une simulation d'un liquide qui applique un poussee
    # d'archimède lorsque les particules sont sous une certaine hauteur
    #forces_generales.append(ForcePousseeArchimede(5,0.25**2,-10))

    particules : list[Particule] = []

    forces : list[Force] = []
    
    liens : list[Lien] = []

    generateurs_de_collisions : list[GenerateurDeCollisions] = []
    generateurs_de_collisions.append(Sol(particules, -15))
    generateurs_de_collisions.append(DetecteurDeCollisions(particules))

    contacts : list[Contact] = []
    resolveur = ResolveurDeContacts()
    
    # Construire un echafaudage
    # STEPS = Le nombre de cotés de l'echafaudage
    # SUBSTEPS = La densite de l'echafaudage verticalement (une hauteur de 10 totale)
    STEPS = 4
    SUBSTEPS = 4
    angle_step = math.pi / STEPS * 2
    for i in range(STEPS):
        angle = i * angle_step
        pos = Matrice3x3.rotation_Y(angle) * Vecteur3(0,0,-2)
        for j in range(SUBSTEPS):
            particules.append(Particule(1, pos + Vecteur3(0,10/(SUBSTEPS-1),0) * j))
    for i in range(STEPS):
        # Liens solides (Barres)
        for j in range(SUBSTEPS):
            if j < SUBSTEPS-1:
                # Liens verticaux
                liens.append(Barre(particules[i*SUBSTEPS+j],particules[i*SUBSTEPS+j+1]))
                # Liens diagonaux
                liens.append(Barre(particules[(i-1)*SUBSTEPS+j+1],particules[i*SUBSTEPS+j]))
                liens.append(Barre(particules[(i-1)*SUBSTEPS+j],particules[i*SUBSTEPS+j+1]))
            # Liens horizontaux
            liens.append(Barre(particules[(i-1)*SUBSTEPS+j],particules[i*SUBSTEPS+j]))
            # Liens diagonaux entres les "bases" de chaque hauteur
            liens.append(Barre(particules[(i-STEPS//2)*SUBSTEPS+j],particules[i*SUBSTEPS+j]))
        # Ajouter un propulseur sur chaque element de la base de la forme
        forces.append(ForcePropulseur(particules[i*SUBSTEPS],Vecteur3(0,50*SUBSTEPS,0)))
    
    # Particules lourdes pour tester les collisions
    particules.append(Particule(10, Vecteur3(10,-5,0)))
    particules.append(Particule(20, Vecteur3(10.1,10,0)))

    running = True
    paused = True
    souris_capturee = False
    deltaTime = 0

    # Load le font Consolas
    consolas = pg.font.SysFont("Consolas",16)

    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE:
                    paused = not paused
                elif e.key == pg.K_ESCAPE:
                    pg.mouse.set_visible(souris_capturee)
                    souris_capturee = not souris_capturee
                    pg.event.set_grab(souris_capturee)
        
        matrice_camera, camera_position = cameraman.freecam(deltaTime)

        fenetre.fill((0,64,175))

        for force in forces:
            if not paused:
                force.appliquer(deltaTime)
            force.afficher(fenetre, matrice_camera, -camera_position)
        
        for lien in liens:
            if not paused:
                lien.generer_contacts(contacts)
            lien.afficher(fenetre,matrice_camera, -camera_position)
        
        for generateur in generateurs_de_collisions:
            if not paused:
                generateur.generer_contacts(contacts)
            generateur.afficher(fenetre,matrice_camera,camera_position)

        if not paused:
            resolveur.resoudre_contacts(contacts,deltaTime)

        # Trier les particules en ordre du plus petit au plus grand
        # On copie superficiellement la liste pour eviter de changer l'ordre de la vraie liste
        particules_sorted : list[Particule] = particules.copy()
        particules_sorted.sort(key=lambda a: appliquer_transformation(a.position,matrice_camera,camera_position).z,reverse=True)
        for particule in particules_sorted:
            if not paused:
                # Appliquer les forces generales et les afficher
                for force in forces_generales:
                    force.appliquer(particule, deltaTime)
                    force.afficher(particule, fenetre, matrice_camera, -camera_position)
                # Integrer le mouvement de la particule
                particule.integrer(deltaTime)
            # Chaque particule a une couleur unique et aleatoire
            rand.seed(particule.__hash__())
            particule.afficher_point((rand.randint(0,255),rand.randint(0,255),rand.randint(0,255)), fenetre, matrice_camera, -camera_position)
        
        # Écrire les details de la simulation dans les coins de l'écran
        fps = clock.get_fps()
        fenetre.blit(consolas.render(f"FPS: {fps:2g}",False,(64,255,64)),(0,0))
        fenetre.blit(consolas.render(f"Contacts: {len(contacts):3d}",False,(64,255,64)),(fenetre.get_width()-120,0))

        contacts.clear()
        
        pg.display.flip()

        deltaTime = clock.tick(FPS) / 1000