import pygame as pg
import random as rand
from phusikos import *
import utilitees as utils

FPS = 60

pg.init()
fenetre = pg.display.set_mode((700, 700))
clock = pg.time.Clock()

cameraman = utils.Cameraman()

if __name__ == "__main__":
    forces_generales : list[ForceGenerale] = []
    forces_generales.append(ForceGravite())

    # Trainee aerienne (friction de l'air)
    #forces_generales.append(ForceTrainee(0.005, 0.0001))

    # Une simulation d'un liquide qui applique un poussee
    # d'archimède lorsque les particules sont sous une certaine hauteur
    #forces_generales.append(ForcePousseeArchimede(5,-10))

    particules : list[Particule] = []

    forces : list[Force] = []
    
    liens : list[Lien] = []

    generateurs_de_collisions : list[GenerateurDeCollisions] = []
    generateurs_de_collisions.append(Sol(particules, -15))
    generateurs_de_collisions.append(DetecteurDeCollisions(particules,0))

    contacts : list[Contact] = []
    resolveur = ResolveurDeContacts()
    
    utils.construire_echafaudage(3, 2, 3, particules, liens, forces, Barre, Vecteur3(10,0,0), masse=0.5)

    STEPS = 4
    SUBSTEPS = 4
    utils.construire_echafaudage(STEPS, SUBSTEPS, 10, particules, liens, forces, Barre)

    particules.append(Particule(0,Vecteur3(0,10,0),rayon=1))
    for i in range(STEPS):
        liens.append(Cable(particules[-1],particules[-(i*SUBSTEPS)-2],10,1))
    
    particules.append(Particule(0,Vecteur3(10,5,0),rayon=0.5))
    forces.append(ForceBungee(particules[0],particules[-1],20))

    running = True
    paused = True
    souris_capturee = False
    deltaTime = 0

    # Load le font Consolas
    consolas = pg.font.SysFont("Consolas",12)

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

        if deltaTime >= 1/10:
            deltaTime *= 0.25

        fenetre.fill((0,64,175))

        for generateur in generateurs_de_collisions:
            if not paused:
                generateur.generer_contacts(contacts)
            generateur.afficher(fenetre,matrice_camera,-camera_position)

        for force in forces:
            if not paused:
                force.appliquer(deltaTime)
            force.afficher(fenetre, matrice_camera, -camera_position)
        
        for lien in liens:
            if not paused:
                lien.generer_contacts(contacts)
            lien.afficher(fenetre,matrice_camera, -camera_position)

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
        fenetre.blit(consolas.render(f"FPS: {fps:2g}",True,(64,255,64)),(0,0))
        fenetre.blit(consolas.render(f"Contacts: {len(contacts):3d}",True,(64,255,64)),(fenetre.get_width()-100,0))
        fenetre.blit(consolas.render("WASD -> bouger, E ou Q -> monter/descendre, ESC -> capturer/libérer",True,(64,255,64)),(2,fenetre.get_height()-32))
        fenetre.blit(consolas.render("SPACE -> pause/resume, 1234 -> activer propulseurs",True,(64,255,64)),(2,fenetre.get_height()-16))

        contacts.clear()
        
        pg.display.flip()

        deltaTime = clock.tick(FPS) / 1000