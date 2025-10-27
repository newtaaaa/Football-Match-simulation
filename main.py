import random
import pygame
import time
from tasmin import *
from astar import *
import closest_point

pygame.init()
# Caractéristiques du terrain
terrain_longueur = 800  # en mètres
terrain_largeur = 600  # en mètres
largeur = 800
hauteur = 600
fenetre = pygame.display.set_mode((largeur, hauteur))
ballon_image = pygame.image.load("ballon.webp")
ballon_image = pygame.transform.scale(ballon_image, (50, 50))
pygame.display.set_caption("Simulation match")
terrain_image = pygame.image.load("terrain.jpg")
terrain_image = pygame.transform.scale(terrain_image, (800, 600))
panneau_image = pygame.image.load("panneau.png")
psg_img = pygame.image.load("psg.png")
psg_img = pygame.transform.scale(psg_img, (50, 50))
madrid_img = pygame.image.load("madrid.png")
madrid_img = pygame.transform.scale(madrid_img, (50, 50))
gardien_img = pygame.image.load("gardien.png")
gardien_img = pygame.transform.scale(gardien_img, (70, 70))
ballon_cord = (0, 0)
clock = pygame.time.Clock()
frame_rate = 10
font = pygame.font.Font(None, 36)
but_equipe1_x, but_equipe1_y = 40, terrain_largeur // 2
but_equipe2_x, but_equipe2_y = 730, terrain_largeur // 2
un_contact_par_minute = 0
score_rect = pygame.Rect(300, 10, 200, 50)  # Position et taille du rectangle
time_rect = pygame.Rect(505, 10, 50, 50)
tiempo = 0
pygame.mixer.init()

# Charger le fichier .wav
pygame.mixer.music.load('psg.wav')

# Jouer la musique en boucle
pygame.mixer.music.play(-1)


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def collision_joueurs(joueur, equipe_adv):
    if joueur.porteur_de_balle:
        for joueur_adv in equipe_adv.joueurs:
            if joueur.rect.colliderect(joueur_adv.rect):
                if random.random() < 0.2 + (max(joueur.defense, joueur_adv.defense)) / 200:
                    if joueur.defense > joueur_adv.defense:
                        print("plus puissant\n")
                        return None
                    else:
                        print("défendu\n")
                        return joueur_adv
                print("récuperation classique\n")
                return joueur_adv
    else:
        return None


def pos_balle(equipe_adv):
    if equipe_adv.get_porteur_de_balle() is not None:
        return equipe_adv.get_porteur_de_balle().coord
    else:
        return None


def proba(tir, arret, dist):
    """Retourne la probabilité de marquer un but en fonction de la précision du tir,
    de la compétence du gardien et de la distance au but."""
    tir_norm = tir / 100
    arret_norm = arret / 100
    # Calcul de la base de la probabilité
    base_prob = (tir_norm - arret_norm) / (1 + dist / 50)
    # Transformation sigmoïde pour obtenir une probabilité entre 0 et 1
    prob = 1 / (1 + math.exp(-base_prob * 5))  # Ajustement de la sensibilité avec * 5
    # Ajustement final pour que la probabilité tende vers 0 quand la distance augmente
    adjusted_prob = prob * math.exp(-dist / 300)
    return adjusted_prob


class Gardien:
    def __init__(self, reflexe, numero):
        self.reflexe = reflexe
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.numero = numero
        if self.numero == 1:
            self.coord = (50, 295)
        else:
            self.coord = (685, 295)

    def position(self, ballon_coord):
        x, y = self.coord
        b = random.uniform(0, 6)
        # Gardien se déplace uniquement en Y en fonction de la position Y du ballon
        if y < ballon_coord[1]:
            if y > 330:
                y -= b
            else:
                y += b
        elif y > ballon_coord[1]:
            if y < 245:
                y += b
            else:
                y -= b
        # Assurez-vous que le gardien reste dans les limites du terrain
        y = max(10, min(y, terrain_largeur - 10))
        self.coord = (x, y)
        self.rect.x, self.rect.y = x, y
        fenetre.blit(gardien_img, (self.rect.x, self.rect.y))


class Joueur:
    def __init__(self, precision, vitesse, defense, passe, distance_tir, poste):
        self.precision_tir = precision
        self.vitesse = vitesse
        self.defense = defense
        self.coord = (0, 0)
        self.porteur_de_balle = False
        self.distance_tir = distance_tir
        self.passe = passe
        self.poste = poste
        self.rect = pygame.Rect(0, 0, 30, 30)

    def tir_au_but(self, equipe_num):
        """Le joueur est a distance raisonnable du but adverse"""
        distance_joueur_x, distance_joueur_y = self.coord
        if equipe_num == 1:
            distance_but = math.sqrt(
                (distance_joueur_x - but_equipe2_x) ** 2 + (distance_joueur_y - but_equipe2_y) ** 2)
        else:
            distance_but = math.sqrt(
                (distance_joueur_x - but_equipe1_x) ** 2 + (distance_joueur_y - but_equipe1_y) ** 2)

        return distance_but <= self.distance_tir


    def position(self, num_equipe, equipe, equipe_adv):
        if self.poste == "atkg":
            vitesse = self.vitesse
            x, y = self.coord
            a = random.uniform(0, vitesse - 20)
            b = random.uniform(-20, 20)
            dist = 1000
            if equipe.equipe_balle:
                if num_equipe == 1:
                    if x + a >= terrain_longueur - 80:
                        x = terrain_longueur - 80
                    else:
                        x += a
                else:
                    if x - a <= 60:
                        x = 60
                    else:
                        x -= a
                if y + b >= terrain_largeur - 55:
                    y = terrain_largeur - 55
                elif y + b <= 45:
                    y = 45
                else:
                    y += b
                self.coord = (x, y)
                self.rect.x, self.rect.y = x, y
            else:
                equipe.position2(self, equipe_adv, dist)
            equipe.motif()

class Equipe:
    def __init__(self, numero, joueurs, gardien):
        self.numero = numero
        self.joueurs = joueurs
        self.gardien = gardien
        self.score = 0
        self.equipe_balle = False
        self.strategie = File()

    def prio_equipe(self):
        """ donner la balle au joueur le plus proche du but adverse """
        global ballon_cord
        tas_prio = Tas()
        for joueur in self.joueurs:
            if joueur.porteur_de_balle:
                continue
            if self.numero == 2:
                dist = distance(joueur.coord, [but_equipe1_x, but_equipe1_y])
            else:
                dist = distance(joueur.coord, [but_equipe2_x, but_equipe2_y])
            tas_prio.tasmin_push(joueur, dist)
        return tas_prio

    def remplir_graphe(self):
        g = Graph()
        alpha = 40
        g.set_graphe(self.joueurs)
        for i in range(len(self.joueurs)):
            for j in range(i + 1, len(self.joueurs)):
                weight = distance(self.joueurs[i].coord, self.joueurs[j].coord)
                if self.joueurs[i].passe + alpha > weight//2 + 20:
                    g.add_edge(self.joueurs[i], self.joueurs[j], weight)
        return g

    def dessiner_arcs(self):
        g = self.remplir_graphe()
        for u in g.graph:
            for (v, weight) in g.graph[u]:
                pos1 = u.coord
                pos2 = v.coord
                if self.numero == 1:
                    pygame.draw.circle(fenetre, (0,255,0), pos1, 10)
                    pygame.draw.line(fenetre, (0, 255, 0), pos1, pos2, 2)
                else:
                    pygame.draw.circle(fenetre, (255, 255, 0), pos1, 10)
                    pygame.draw.line(fenetre, (255, 255, 0), pos1, pos2, 2)

    def replacement(self):
        for joueur in self.joueurs:
            if joueur.poste == "atkg":
                if self.numero == 1:
                    a, b = (338, 167)
                else:
                    a, b = (462, 167)
                joueur.coord = a, b
                joueur.rect.x = a
                joueur.rect.y = b
            elif joueur.poste == "atkd":
                if self.numero == 1:
                    a, b = (354, 391)
                else:
                    a, b = (462, 391)
                joueur.coord = a, b
                joueur.rect.x = a
                joueur.rect.y = b
        lead = a, b
        for j in self.joueurs:
            if j.poste != "atkg" or j.poste != "atkd":
                x, y = lead
                if self.numero == 1:
                    if j.poste == "def":
                        x -= 150
                        y += 200
                    x -= 100
                    if j.poste == "midd":
                        y += 200
                    else:
                        y -= 200
                else:
                    if j.poste == "def":
                        x += 125
                        y += 200
                    x += 60
                    if j.poste == "midd":
                        y += 200
                    else:
                        y -= 200
                j.coord = (x, y)
                j.rect.x, j.rect.y = x, y

    def afficher_joueurs(self):
        for joueur in self.joueurs:
            if self.numero == 2:
                pygame.draw.rect(fenetre, (255, 0, 0), joueur.rect)
                #fenetre.blit(psg_img, joueur.rect)
            else:
                pygame.draw.rect(fenetre, (0, 0, 255), joueur.rect)
                #fenetre.blit(madrid_img, joueur.rect)
    def animation(self, passeur, destinataire, equipe_adverse, but):
        global ballon_cord
        start_x, start_y = passeur.coord  # La position du joueur qui a tiré
        if destinataire is not None:
            end_x, end_y = int(destinataire.coord[0]), int(destinataire.coord[1])
        else:
            if self.numero == 1:
                end_x, end_y = but_equipe2_x, but_equipe2_y
            else:
                end_x, end_y = but_equipe1_x, but_equipe1_y
        steps = 25  # Nombre d'étapes pour l'animation de la trajectoire du tir
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        for _ in range(steps):
            start_x += dx
            start_y += dy
            ballon_cord = (start_x, start_y)
            fenetre.blit(terrain_image, (0, 0))  # Effacez l'image précédente
            fenetre.blit(ballon_image, (ballon_cord[0], ballon_cord[1]))  # Affichez le ballon
            self.afficher_joueurs()
            equipe_adverse.afficher_joueurs()
            self.gardien.position(ballon_cord)
            equipe_adverse.gardien.position(ballon_cord)
            self.dessiner_arcs()
            equipe_adverse.dessiner_arcs()

            if self.numero == 1:
                score_text = font.render(f"Score : {self.score} - {equipe_adverse.score}", True, (255, 255, 255))
            else:
                score_text = font.render(f"Score : {equipe_adverse.score} - {self.score}", True, (255, 255, 255))
            time_text = font.render(f"{tiempo//2}'", True, (255, 255, 255))
            pygame.draw.rect(fenetre, (0, 0, 0), score_rect)  # Couleur du rectangle (ici noir)
            pygame.draw.rect(fenetre, (0, 0, 0), time_rect)
            fenetre.blit(score_text, (330, 20))
            fenetre.blit(time_text, (517, 20))

            pygame.display.update()
            if destinataire is None:
                pygame.time.delay(15)  # Délai pour l'animation
            else:
                pygame.time.delay(20)
        if not but and destinataire is None:
            if equipe_adverse.numero == 2:
                ballon_cord = 700, equipe_adverse.gardien.coord[1]
            else:
                ballon_cord = equipe_adverse.gardien.coord
            fenetre.blit(terrain_image, (0, 0))  # Effacez l'image précédente
            fenetre.blit(ballon_image, (ballon_cord[0], ballon_cord[1]))  # Affichez le ballon
            self.afficher_joueurs()
            equipe_adverse.afficher_joueurs()
            self.gardien.position(ballon_cord)
            equipe_adverse.gardien.position(ballon_cord)
            self.dessiner_arcs()
            equipe_adverse.dessiner_arcs()

            if self.numero == 1:
                score_text = font.render(f"Score : {self.score} - {equipe_adverse.score}", True, (255, 255, 255))
            else:
                score_text = font.render(f"Score : {equipe_adverse.score} - {self.score}", True, (255, 255, 255))
            time_text = font.render(f"{tiempo//2}'", True, (255, 255, 255))
            pygame.draw.rect(fenetre, (0, 0, 0), score_rect)  # Couleur du rectangle (ici noir)
            pygame.draw.rect(fenetre, (0, 0, 0), time_rect)
            fenetre.blit(score_text, (330, 20))
            fenetre.blit(time_text, (517, 20))
            pygame.display.update()
            time.sleep(1)
    def get_porteur_de_balle(self):
        for joueur in self.joueurs:
            if joueur.porteur_de_balle:
                return joueur
        return None

    def changer_porteur(self, joueur, joueur_adv, equipe_adverse):
        joueur.porteur_de_balle = False
        self.equipe_balle = False
        joueur_adv.porteur_de_balle = True
        equipe_adverse.equipe_balle = True

    def mouvements(self, equipe_adverse):
        global ballon_cord
        global un_contact_par_minute
        but = False

        # Vérifier s'il y a déjà un porteur de balle dans l'équipe

        for joueur in self.joueurs:
            joueur.position(self.numero, self, equipe_adverse)
            joueur_adv = collision_joueurs(joueur, equipe_adverse)

            if joueur_adv is not None and un_contact_par_minute == 0:
                un_contact_par_minute = 1
                self.changer_porteur(joueur, joueur_adv, equipe_adverse)

            if random.random() < 0.5 and joueur.porteur_de_balle:
                porteur = self.passer_balle(joueur)
                if porteur != None:
                    self.animation(joueur, porteur, equipe_adverse, but)

            if joueur.porteur_de_balle and joueur.tir_au_but(self.numero):
                if self.numero == 1:
                    prob = proba(joueur.precision_tir, equipe_adverse.gardien.reflexe, distance(joueur.coord, [but_equipe2_x, but_equipe2_y]))
                else:
                    prob = proba(joueur.precision_tir, equipe_adverse.gardien.reflexe,
                                 distance(joueur.coord, [but_equipe1_x, but_equipe1_y]))
                if prob > random.random():
                    but = True
                    self.score += 1
                    print(f"But du joueur {self.joueurs.index(joueur) + 1} pour l'équipe {self.numero} !")
                    self.animation(joueur, None, equipe_adverse, but)
                    joueur_adv = random.choice(equipe_adverse.joueurs)
                    self.changer_porteur(joueur, joueur_adv, equipe_adverse)
                    break
                else:
                    but = False
                    self.animation(joueur, None, equipe_adverse, but)
                    joueur_adv = random.choice(equipe_adverse.joueurs)
                    self.changer_porteur(joueur, joueur_adv, equipe_adverse)
                    self.replacement()
                    equipe_adverse.replacement()

        self.afficher_joueurs()
        self.dessiner_arcs()
        for joueur in self.joueurs:
            if joueur.porteur_de_balle:
                ballon_cord = (joueur.coord[0], joueur.coord[1])
                fenetre.blit(ballon_image, (ballon_cord[0], ballon_cord[1]))
        self.gardien.position(ballon_cord)
        return but

    def passer_balle(self, porteur):
        """donner la balle au joueur prioritaire"""
        g = self.remplir_graphe()
        prio = self.prio_equipe()
        meilleur_choix = prio.peek()
        liste = g.graph[porteur]
        nouveau = None
        joueurs = [joueur for joueur, w in liste]
        if (porteur.passe // 400) > random.random():
            nouveau = meilleur_choix
        elif joueurs != []:
            # choix destinataire aléatoire
            #nouveau = random.choice(joueurs)
            # passe au plus proche
            """coord = [joueur.coord for joueur in joueurs]
            joueur_proche_coord = closest_point.closest_point_to_given_point(coord, porteur.coord)
            nouveau = [joueur for joueur in joueurs if joueur.coord == joueur_proche_coord][0]"""
            # enchainement de passes
            alea = random.random()
            if alea + 80 > random.random():
                tas = self.prio_equipe()
                chemin = g.a_star(porteur, tas.tasmin_pop())
                if self.strategie.estVide() and chemin is not None:
                    for joueur in chemin:
                        self.strategie.enfiler(joueur)
                else:
                    self.strategie.defiler()
                    nouveau = self.strategie.peek()
            else:
                coord = [joueur.coord for joueur in joueurs]
                joueur_proche_coord = closest_point.closest_point_to_given_point(coord, porteur.coord)
                nouveau = [joueur for joueur in joueurs if joueur.coord == joueur_proche_coord][0]
        else:
            nouveau = None
        if nouveau != None:
            porteur.porteur_de_balle = False
            nouveau.porteur_de_balle = True
        return nouveau

    def motif(self):
        for j in self.joueurs:
            if j.poste == "atkg":
                lead = j.coord
                lead_x, lead_y = lead
                break

        for j in self.joueurs:
            if j.poste != "atkg":
                x, y = lead_x, lead_y  # Initialiser avec les coordonnées du meneur
                a = random.uniform(0, j.vitesse - 20)
                b1 = random.uniform(0, 20)
                b2 = random.uniform(-20, 0)

                if self.numero == 1:
                    if j.poste == "def":
                        x -= 150 - a  # Augmenter l'aléa
                        y += 200 + b1  # Augmenter l'aléa
                        if y >= terrain_largeur - 55:
                            y = terrain_largeur - 55
                    elif j.poste != "atkd":
                        x -= 100 - a  # Augmenter l'aléa
                    if x > terrain_longueur - 80:
                        x = terrain_longueur - 80
                    if x < 60:
                        x = 60
                    if j.poste == "midd":
                        y += 210 + b1  # Augmenter l'aléa
                        if y >= terrain_largeur - 55:
                            y = terrain_largeur - 55
                    else:
                        y -= 200 + b2  # Augmenter l'aléa
                        if y <= 45:
                            y = 45
                else:
                    if j.poste == "def":
                        x += 150 + a  # Augmenter l'aléa
                        y += 200 + b1  # Augmenter l'aléa
                        if y >= terrain_largeur - 55:
                            y = terrain_largeur - 55
                    elif j.poste != "atkd":
                        x += 40 + a  # Augmenter l'aléa
                    if x > terrain_longueur - 80:
                        x = terrain_longueur - 80
                    if x < 60:
                        x = 60
                    if j.poste == "midd":
                        y += 200 + b1  # Augmenter l'aléa
                        if y >= terrain_largeur - 55:
                            y = terrain_largeur - 55
                    else:
                        y -= 200 + b2  # Augmenter l'aléa
                        if y <= 45:
                            y = 45
                if j.poste == "atkd":
                    y += 300 + b1
                    if y >= terrain_largeur - 55:
                        y = terrain_largeur - 55
                    if y <= 45:
                        y = 45
                j.coord = (x, y)
                j.rect.x, j.rect.y = x, y

    def position2(self, joueur, equipe_adv, dist_max):
        if joueur.poste == "atkg":
            x, y = joueur.coord
            a = random.uniform(0, joueur.vitesse - 20)
            b1 = random.uniform(0, 20)
            b2 = random.uniform(-20, 0)
            ballon = pos_balle(equipe_adv)
            if distance(joueur.coord, ballon) < dist_max:
                if ballon[0] > joueur.coord[0]:
                    if x + a >= terrain_longueur - 80:
                        x = terrain_longueur - 80
                    else:
                        x += a
                else:
                    if x - a <= 60:
                        x = 60
                    else:
                        x -= a
                if ballon[1] > joueur.coord[1]:
                    if y + b1 >= terrain_largeur - 55:
                        y = terrain_largeur - 55
                    else:
                        y += b1
                else:
                    if y + b2 <= 45:
                        y = 45
                    else:
                        y += b2
                joueur.coord = (x, y)
                joueur.rect.x, joueur.rect.y = x, y


equipe1 = Equipe(1, [Joueur(90, 71, 65, 80, 180, "atkg"), Joueur(71, 67, 68, 80, 180, "midd"), Joueur(69, 71, 67, 80, 180, "midg"),
                     Joueur(87, 71, 67, 80, 180, "def"), Joueur(90, 71, 65, 80, 180, "atkd")], Gardien(1, 1))
equipe2 = Equipe(2, [Joueur(81, 65, 69, 80, 180, "def"), Joueur(71, 67, 68, 69, 180, "midd"), Joueur(69, 71, 67, 69, 180, "midg"),
                     Joueur(87, 71, 67, 100, 180, "atkg"), Joueur(90, 71, 65, 80, 180, "atkd")], Gardien(1, 2))
equipe1.replacement()
equipe2.replacement()
equipe1.joueurs[0].porteur_de_balle = True
equipe1.equipe_balle = True


while True:
    tiempo += 1
    fenetre.blit(terrain_image, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    but_equipe1 = equipe1.mouvements(equipe2)
    if but_equipe1:
        equipe1.replacement()
        equipe2.replacement()
    but_equipe2 = equipe2.mouvements(equipe1)
    un_contact_par_minute = 0
    if but_equipe2:
        equipe1.replacement()
        equipe2.replacement()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if tiempo >= 183 + random.randint(2, 6) and equipe2.score - equipe1.score != 0:
        break

    # Afficher les coordonnées de la souris dans la console
    #print(f"Position de la souris : ({mouse_x}, {mouse_y})")
    score_text = font.render(f"Score : {equipe1.score} - {equipe2.score}", True, (255, 255, 255))
    time_text = font.render(f"{tiempo // 2}'", True, (255, 255, 255))
    pygame.draw.rect(fenetre, (0, 0, 0), score_rect)  # Couleur du rectangle (ici noir)
    pygame.draw.rect(fenetre, (0, 0, 0), time_rect)
    fenetre.blit(score_text, (330, 20))
    fenetre.blit(time_text, (517, 20))
    pygame.display.update()
    clock.tick(frame_rate)

score_equipe1, score_equipe2 = equipe1.score, equipe2.score
print(f"Score final : {score_equipe1} - {score_equipe2}")
time.sleep(8)
pygame.mixer.music.stop()
pygame.quit()
