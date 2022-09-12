import random
import numpy as np
import copy
from CLSP import CLSP
import time
import tkinter
import tkinter.filedialog
import ntpath
import os


class CLSP_GA:

    def __init__(self, path, filename, pop_size, par_percentage, mutation_prob):
        self.population_size = pop_size
        self.percentage = par_percentage
        self.p_mutation = mutation_prob
        self.population = []
        self.totalCostList = []
        self.parent_list = [] #list of indices of individuals selected for breeding
        self.myCLSP = CLSP(path, filename)
        self.population.append(self.myCLSP.generateDemandList())
        self.totalCostList.append(self.myCLSP.planDemandList(self.population[0]))
        self.timeList = []
        self.start_time = time.time()

        i = 1
        while i < self.population_size:
            pot_indiv = self.population[0]
            pot_indiv = pot_indiv.copy()
            #print(pot_indiv)
            #print(self.population[0])
            random.seed()
            random.shuffle(pot_indiv)

            indiv_valid = True #here we're checking if the individual is already in the population list
            for j in range(len(self.population)):
                if pot_indiv == self.population[j]:
                    indiv_valid = False
                    break

            if indiv_valid:
                self.totalCostList.append(self.myCLSP.planDemandList(pot_indiv))
                #print("This is individual's cost:", self.totalCostList[i])
                self.population.append(pot_indiv)
                i += 1

    def select_parents(self):
        pop_size    = len(self.population)
        num_parents = round(pop_size * self.percentage)

        while len(self.parent_list) < num_parents:
            remaining_pop = list(range(pop_size))
            remaining_pop = [x for x in remaining_pop if x not in self.parent_list]
            #print(remaining_pop)
            parent_cands  = random.sample(remaining_pop, 2)
            #print(parent_cands)

            new_parent = parent_cands[0]
            if self.totalCostList[parent_cands[0]] > self.totalCostList[parent_cands[1]]:
                new_parent = parent_cands[1]

            self.parent_list.append(new_parent)
        print("individuals", self.parent_list, "were chosen as parents for breeding.")

    def crossover(self):
        children_list = []
        child = self.population[0]
        child = child.copy()

        for i in range(0, len(self.parent_list) - 1, 2):
            parents = [self.parent_list[i], self.parent_list[i+1]]
            heart_start = round(len(self.population[0])/3)
            heart_end   = round(len(self.population[0])/3*2)
            #print(parents)

            for j in range(2):
                heart   = self.population[parents[0]][heart_start:heart_end]
                heart   = heart.copy()
                fill_up = self.population[parents[1]]
                fill_up = fill_up.copy()

                #print("heart = ", heart)
                #print("fill_up = ", fill_up)
                fill_up1 = fill_up.copy()
                fill_up[:heart_start], fill_up[heart_start:] = fill_up1[heart_end:], fill_up1[:heart_end]
                #print("fill_up = ", fill_up)
                fill_up = [x for x in fill_up if x not in heart]
                #print("fill_up = ", fill_up)
                child[:heart_start]          = fill_up[heart_start:]
                child[heart_start:heart_end] = heart
                child[heart_end:]            = fill_up[:heart_start]
                child                        = child.copy()
                #print("child = ", child)

                self.population.append(child)
                children_list.append(child)
                #print(children_list)
                self.totalCostList.append(self.myCLSP.planDemandList(child))
                #child.planDemandList(demand)
                #child.update_totalCost()
                #print(child.totalCost)
                parents.reverse()

        print(len(children_list), "children were generated from", len(self.parent_list), "parents.")
        print("Population is of the size",len(self.population))


    def mutate(self):
        mutations_swap = 0
        mutations_shift = 0
        num_mutations = round(len(self.population)*self.p_mutation)
        all_indivs = list(range(self.population_size))
        mut_indivs = random.sample(all_indivs, num_mutations)

        for indiv in mut_indivs:

            if np.random.random() < 0.5:
                self.mutate_swap(indiv)
                mutations_swap += 1
            else:
                self.mutate_pop_insert(indiv)
                mutations_shift += 1

        print(mutations_swap, "individuals have a swap mutation.")
        print(mutations_shift, "individuals have a pop–insert mutation.")

    def mutate_swap(self, indiv):
        all_indices = list(range(len(self.population[0])))
        indices = random.sample(all_indices, 2)

        self.population[indiv][indices[0]], self.population[indiv][indices[1]] = self.population[indiv][indices[1]], self.population[indiv][indices[0]]
        self.totalCostList[indiv] = self.myCLSP.planDemandList(self.population[indiv])

    def mutate_pop_insert(self, indiv):
        all_indices = list(range(len(self.population[0])))
        indices = random.sample(all_indices, 2)

        popped = self.population[indiv].pop(indices[0])
        self.population[indiv].insert(indices[1], popped)
        self.totalCostList[indiv] = self.myCLSP.planDemandList(self.population[indiv])

    def update_population(self):
        min_indList = []
        for i in range(len(self.population) - self.population_size):
            min_index = self.totalCostList.index(max(self.totalCostList))
            del self.totalCostList[min_index]
            del self.population[min_index]
            min_indList.append(min_index)
        end_time = time.time()
        self.timeList.append(end_time - self.start_time)

        print("Size of the population is", len(self.population))
        print("This is the total cost list:", sorted(self.totalCostList))
        print("Time to get the solution is:", self.timeList[-1], "seconds")

population = [50, 100, 200]
parent_fraction = [0.2, 0.3, 0.4]
mutation_probability = [0.05, 0.10]
number_of_generations = [300, 500]
time_list = []
obj_value_list = []

open_opt = options = {}
options['defaultextension'] = '.txt'
options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
options['initialdir'] = 'C:\\'
options['initialfile'] = 'Output.txt'
#options['parent'] = 'none'
options['title'] = 'Open input file'

filelist = tkinter.filedialog.askopenfilenames(**open_opt)

print(filelist)

save_opt = options = {}
options['defaultextension'] = '.txt'
options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
options['initialdir'] = 'C:\\'
options['initialfile'] = 'Output.txt'
#options['parent'] = root
options['title'] = 'Save output file'
savefile = tkinter.filedialog.asksaveasfile(mode='w', **save_opt)
for file in filelist:
    for pop_size in population:
        for parent_fract in parent_fraction:
            for mut_prob in mutation_probability:

                filename = os.path.split(file)[1]
                start_time = time.time()
                myCLSP_GA = CLSP_GA('', file, pop_size, parent_fract, mut_prob)

                for gen in number_of_generations:
                    for i in range(gen):
                        myCLSP_GA.select_parents()
                        myCLSP_GA.crossover()
                        myCLSP_GA.mutate()
                        myCLSP_GA.update_population()
                    end_time = time.time()
                    time_list.append(round(end_time - start_time, 3))
                    sorted_cost_list = sorted(myCLSP_GA.totalCostList).copy()
                    obj_value_list.append(sorted_cost_list[0])

                    myoutput = open(savefile.name, "a")
                    #myoutput.write(filename + ',')
                    myoutput.write(str(pop_size) + ' x ' + str(gen) + ' x ' + str(parent_fract * 100) + ' x ' +  str(mut_prob * 100) + ',')
myoutput.write('\n')
myoutput.write(str(obj_value_list) + '\n')
myoutput.write(str(time_list) + '\n')
myoutput.write(str(filelist))

