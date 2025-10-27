import math


def echanger(t, i, j):
    temp = t[i]
    t[i] = t[j]
    t[j] = temp


class Elem:
    def __init__(self, val, prio):
        self.val = val
        self.prio = prio


class Tas:
    def __init__(self):
        self.nb_el = 0
        self.tab_el = []

    def taille_tas(self):
        return self.nb_el

    def est_vide(self):
        return self.nb_el == 0

    def peek(self):
        if not self.est_vide():
            return self.tab_el[0].val

    def fg(self, i):
        return 2 * i + 1

    def fd(self, i):
        return 2 * i + 2

    def pere(self, i):
        return (i - 1) // 2  # Utilisez la division entière avec //

    def monter_noeud(self, i):
        if i != 0 and self.tab_el[self.pere(i)].prio > self.tab_el[i].prio:
            echanger(self.tab_el, i, self.pere(i))
            self.monter_noeud(self.pere(i))

    def descendre_noeud(self, i):
        j = i
        if self.fg(i) < self.nb_el and self.tab_el[self.fg(i)].prio < self.tab_el[j].prio:
            j = self.fg(i)
        if self.fd(i) < self.nb_el and self.tab_el[self.fd(i)].prio < self.tab_el[j].prio:
            j = self.fd(i)
        if i != j:
            echanger(self.tab_el, i, j)
            self.descendre_noeud(j)

    def tasmin_push(self, val, prio):
        e = Elem(val, prio)
        self.tab_el.append(e)
        self.nb_el += 1
        self.monter_noeud(self.nb_el - 1)

    def tasmin_pop(self):
        if self.est_vide():
            return None
        self.nb_el -= 1
        echanger(self.tab_el, 0, self.nb_el)
        self.descendre_noeud(0)
        return self.tab_el[self.nb_el].val


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


class File:
    def __init__(self):
        self.valeurs = []

    def enfiler(self, valeur):
        self.valeurs.append(valeur)

    def defiler(self):
        if self.valeurs:
            return self.valeurs.pop(0)

    def peek(self):
        if self.valeurs:
            return self.valeurs[0]

    def estVide(self):
        return self.valeurs == []

    @property
    def longueur(self):
        return len(self.valeurs)

    def __str__(self):
        ch = "\nEtat de la file:\n"
        for x in self.valeurs:
            ch +=  str(x) + " "
        return ch