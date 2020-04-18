import random

def indice_max(L): # Renvoie l'indice de l'élément de valeur maximum de L
    imax = 0
    for i in range(len(L)):
        if L[i] > L[imax]:
            imax = i
    return imax

def compare(c1, c2): # Renvoie p et m, respectivement le nombre de couleur de c2 bien et mal placé dans c1
    p, m = 0, 0 # On initialise p et m à 0
    for i2 in range(len(c2)): # On parcourt chaque pion de c2 afin de déterminer
        if c2[i2] == c1[i2]: # S'il est de la même couleur que celui de c1 à la même position
            p += 1 # On incrémente alors p de 1 et on passe au pion suivant
        else: # Sinon on va chercher si la couleur de ce pion est tout de même présente à une autre position dans c1
            i1 = (i2+1)%len(c1)
            while i1 != i2: # Tant que i1 n'est pas revenu à i2
                if c2[i2] == c1[i1]: # Si on trouve un pion de c1 de la même couleur
                    m, i1 = m+1, i2 # On incrémente m de 1 et on change la valeur de i1 pour sortir de la boucle while et passer au pion suivant
                else: # Sinon on continue de chercher et on sortira du while quand on aura tout parcouru
                    i1 = (i1+1)%len(c1)
    return p,m # On renvoie p et m

def score(p, m):
    return 2*p+m

def eval(cj, c, score_obtenu):
    pc, mc = compare(c,cj) # On calcule les valeurs de p et m qu'on aurait obtenu avec cj, si c était solution
    return abs(score(pc,mc)-score_obtenu) # On calcule la différence entre le score qu'on aurait obtenu si c était solution
    # et le score obtenu avec la solution. On met une valeur absolue pour n'avoir que des évaluations positives (dans N*)

def fitness(historique_guesses, c, historique_scores): # On calcule le fitness moyen d'un solution candidate c
    sum = 0 # Pour cela on somme les évaluations de c par rapport a chaque guess effectué et au score obtenu
    for i in range(len(historique_guesses)):
        sum += eval(historique_guesses[i], c, historique_scores[i])
    return sum/len(historique_guesses) # On renvoie la moyenne, mais la somme aurait bien fonctionné également

class Game:
    def __init__(self, N, k, solution):
        self.N = N
        self.k = k
        self.solution = solution
        self.guessed = []
        self.scores_obtenus = []
        self.pop = []
        self.fitnesses = []
        self.selected = []

    def guess(self, g): # Fais une proposition g et reçoit la réponse de l'adversaire (p et m)
        # dont le score est calculé et placé dans score obtenu
        p, m = compare(self.solution, g)
        self.guessed.append(g)
        self.scores_obtenus.append(score(p, m))
        return p, m # L'adversaire renvoie p et m

    def gen_pop(self, taille): # Génère une population de taille taille
        self.pop = []
        for i in range(taille):
            self.pop.append([random.randint(1, self.k) for i in range(self.N)])

    def add_fitnesses(self): # Calcule les fitnesses de la population et les ajoute à la liste des fitnesses
        self.fitnesses = []
        for i in range(len(self.pop)):
            self.fitnesses.append(fitness(self.guessed, self.pop[i], self.scores_obtenus))

    def select(self, m): # On selectionne les m combinaisons de la population ayant les meilleurs fitnesses
        temp_list = self.fitnesses[:m]  # On crée une liste temporaire qui au début contient les m premiers éléments de la liste des fitnesses
        self.selected = self.pop[:m] # On attribut à la liste qui contiendra les m meilleurs combinaisons, les m premiers éléments de la population
        imax = indice_max(temp_list)  # On cherche le maximum de la liste temporaire
        for i in range(m, len(self.fitnesses)):  # Pour chacun des autres éléments de la liste des fitnesses
            if self.fitnesses[i] < temp_list[imax]:  # On regarde s'il a sa place dans la liste temporaire (plus petit que le maximum)
                temp_list[imax] = self.fitnesses[i]  # Si c'est le cas, il remplace le maximum de la liste temporaire
                self.selected[imax] = self.pop[i] # On modifie aussi en conséquence la liste des m meilleures combinaisons: self.selected
                imax = indice_max(temp_list)  # Et on calcule le nouveau maximum
        # A présent self.selected contient les m combinaisons de self.pop ayant les fitnesses les plus bas

    def mutation(self): # Effectue des mutations
        for i in range(len(self.selected)):
            for j in range(len(self.selected[0])): # On parcourt tous les pions de chaque combinaison sélectionné
                if random.random() < 0.1: # Avec une certaine probabilité, on change la couleur
                    self.selected[i][j] = random.randint(1,self.k)
                if random.random() < 0.1: # Avec une certaine probabilité, on intervertit deux couleurs
                    k = random.randint(0, self.N-1)
                    self.selected[i][j], self.selected[i][k] = self.selected[i][k], self.selected[i][j]

    def crossover(self): # Effectue des croisements
        length = len(self.selected)
        for i in range(length): # Pour chaque combinaison sélectionnée
            if random.random() < 0.8: # Crossover en un point, avec une certaine probabilité
                j = random.randint(1, length-1) # Pour cela, on choisit une seconde combinaison
                if j != i:
                    k = random.randint(1, self.N-1) # On choisit la position de la césure
                    self.selected.append(self.selected[i][:k]+self.selected[j][k:]) # On crée notre nouvelle combinaison
            if random.random() < 0.8: # Crossover uniforme, avec une certaine probabilité
                j = random.randint(1, length - 1)  # Pour cela, on choisit une seconde combinaison
                if j != i:
                    created = self.selected[i] # On crée une nouvelle combinaison d'abord égale à la première combinaison
                    for k in range(self.N):
                        if random.random() < 0.5:
                            created[k] = self.selected[j][k] # On modifie certains pions par les pions de la deuxième combinaison
                    self.selected.append(created)

    def replace(self): # Remplace l'ancienne population self.pop par la nouvelle self.selected
        self.pop = self.selected

    def best(self): # Retourne le fitness de la meilleure combinaison de la population actuelle et la combinaison correspondante
        mini = min(self.fitnesses)
        i = self.fitnesses.index(mini)
        return mini, self.pop[i]

# Initialisation
N = 4 # Number de pegs
k = 8 # Number of colours
s = [3, 7, 2, 1] # The solution
taille_pop = 10 # Size of the population, > 1
#Start
game = Game(N, k, s) # We create an object to start
i = 1 # Store the number of guesses
j = [] # Store the number of generation by guess
g = [random.randint(1, k) for i in range(N)] # Chose first guess randomly
print("Guess " + str(i) + ": " + str(g))
p,_ = game.guess(g) # First guess
while p != N: # While we haven't won
        j.append(0)
        game.gen_pop(taille_pop) # We generate our population
        game.add_fitnesses() # We compute fitnesses
        fit, g = game.best() # On détermine la combinaison avec le meilleur fitness
        while fit != 0: # On regarde si cette combinaison a un fitness de 0 (condition de sortie)
            j[-1] += 1
            game.select(max(2, int(taille_pop/3))) # Selection of best elements
            game.crossover() # Crossover
            game.mutation() # Mutations
            game.replace() # Population update
            game.add_fitnesses() # We compute fitnesses
            fit, g = game.best() # Retrieve the best possible guess
        # Let's guess
        i += 1
        print("Guess " + str(i) + ": " + str(g))
        p,_ = game.guess(g) # We try a guess
if g == s:
    print("Win, the solution was: ", s)
else:
    print("Lose")
print("Number of guesse(s): ", i)
if len(j) != 0:
    print("Number of generations on average by guess: ", sum(j)/len(j))
    print("Maximum number of generations on average by guess: ", max(j))
