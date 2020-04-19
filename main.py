import random

def index_of_the_max(L): # Return the index of the max value of L
    imax = 0
    for i in range(len(L)):
        if L[i] > L[imax]:
            imax = i
    return imax

def compare(c1, c2): # Return p et m
    p, m = 0, 0
    for i2 in range(len(c2)):
        if c2[i2] == c1[i2]:
            p += 1
        else:
            i1 = (i2+1)%len(c1)
            while i1 != i2:
                if c2[i2] == c1[i1]:
                    m, i1 = m+1, i2
                else:
                    i1 = (i1+1)%len(c1)
    return p,m

def score(p, m): # Compute the score
    return 2*p+m

def eval(cj, c, score_obtenu): # Evaluate c
    pc, mc = compare(c,cj)
    return abs(score(pc,mc)-score_obtenu)

def fitness(historique_guesses, c, historique_scores): # Compute the average fitness of c, if != 0, c has no chance to be the solution
    sum = 0
    for i in range(len(historique_guesses)):
        sum += eval(historique_guesses[i], c, historique_scores[i])
    return sum/len(historique_guesses)

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

    def guess(self, g): # Take a guess and retrieve the p and m values given by the opponent
        p, m = compare(self.solution, g)
        self.guessed.append(g)
        self.scores_obtenus.append(score(p, m))
        return p, m

    def gen_pop(self, size): # Generate a population of a given size
        self.pop = []
        for i in range(size):
            self.pop.append([random.randint(1, self.k) for i in range(self.N)])

    def add_fitnesses(self): # Update self.fitnesses by computing new average fitnesses
        self.fitnesses = []
        for i in range(len(self.pop)):
            self.fitnesses.append(fitness(self.guessed, self.pop[i], self.scores_obtenus))

    def select(self, m): # Select the m best element (with the lowest fitness)
        temp_list = self.fitnesses[:m]
        self.selected = self.pop[:m]
        imax = index_of_the_max(temp_list)
        for i in range(m, len(self.fitnesses)):
            if self.fitnesses[i] < temp_list[imax]:
                temp_list[imax] = self.fitnesses[i]
                self.selected[imax] = self.pop[i]
                imax = index_of_the_max(temp_list)

    def mutation(self): # Carry on mutations
        for i in range(len(self.selected)):
            for j in range(len(self.selected[0])):
                if random.random() < 0.1:
                    self.selected[i][j] = random.randint(1,self.k)
                if random.random() < 0.1:
                    k = random.randint(0, self.N-1)
                    self.selected[i][j], self.selected[i][k] = self.selected[i][k], self.selected[i][j]

    def crossover(self): # Carry out crossovers
        length = len(self.selected)
        for i in range(length):
            if random.random() < 0.8: # One point crossover
                j = random.randint(1, length-1)
                if j != i:
                    k = random.randint(1, self.N-1)
                    self.selected.append(self.selected[i][:k]+self.selected[j][k:])
            if random.random() < 0.8: # Uniform crossover
                j = random.randint(1, length - 1)
                if j != i:
                    created = self.selected[i]
                    for k in range(self.N):
                        if random.random() < 0.5:
                            created[k] = self.selected[j][k]
                    self.selected.append(created)

    def replace(self): # Update the population
        self.pop = self.selected

    def best(self): # Return the best fitness element and his fitness
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
