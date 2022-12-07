import random
import os
import sys
import shutil
import numpy as np

from itertools import cycle
from music21 import converter
from datetime import datetime
from itertools import chain

filepath = 'individuals/'
global is_random 
is_random = True
global needs_first_tuple
needs_first_tuple = False

'''Creates the initial population of random abc individuals. This includes the headers of the abc files as well.'''
def initial_abc_writer(filename):
    t = 'T:' + 'title' + '\n'
    x = 'X:' + '1' + '\n'
    k = 'K:' + 'C' + '\n'
    m = 'M:' + '4/4' + '\n'
    l = 'L:1/8\n'
    r = 'R:' + 'Reel' + '\n'
    q = 'Q:' + 'speed' + '\n'

    header = x + t + m + q + l + r + k
    file_contents = header
    
    note_range = ['c', 'd', 'e', 'f', 'g', 'a', 'b', 'C', 'D', 'E', 'F',
            'G', 'A', 'B', 'c\'', 'd\'', 'e\'', 'f\'', 'g\'', 'a\'', 'b\'']

    accidentals = ['^', '_']

    #starting with the first measure, write music. this is truly random. individuals will be saved in a .abc file
    music = ''
    measures = 0

    while measures < 8:
        beats = 0

        if measures == 0:
            music += 'c2'
            beats += 2

        while beats < 8:
            acc_prob = random.randint(1, 20)

            if (acc_prob >= 19):
                music += ' ' + accidentals[random.randint(0, 1)]

            music += str(random.choice(note_range))
            note_value = random.randint(1, 4)

            if (8-beats) < note_value:
                note_value = 1

            beats += note_value

            if note_value != 1:
                music += str(note_value)

        music += ' | '
        measures += 1

    file_contents += music

    #TEST
    #print(str(filename) + ' contents: ' + file_contents)    
    abcfile = open(filename, 'w')
    abcfile.write(file_contents)
    abcfile.close() 

'''Writes the offspring to files overriding previous generation's files. This method
also implements the header as well as the generated indivuals'''
def abc_writer(filename, notes):
    t = 'T:' + 'title' + '\n'
    x = 'X:' + '1' + '\n'
    k = 'K:' + 'C' + '\n'
    m = 'M:' + '4/4' + '\n'
    l = 'L:1/8\n'
    r = 'R:' + 'Reel' + '\n'
    q = 'Q:' + 'speed' + '\n'

    header = x + t + m + q + l + r + k
    file_contents = header

    measure = 0
    global needs_first_tuple
    if needs_first_tuple == True:
        path = filepath + filename[0]
        #print('filename for writer: ', path)
        offspring = open(path, 'w')
    
    else:
        offspring = open(filepath + filename, 'w')

    offspring.write(header)
    while measure < len(notes):
        if measure == len(notes) - 1:
            offspring.write(notes[measure])
        else:
            offspring.write(notes[measure] + ' | ')
        measure += 1

    
    offspring.close()

'''randomly initializes a population
uses initial_abc_writer()'''
def pop_initialization(num_of_individuals):
    count = 1

    while count <= num_of_individuals:
        title = 'individuals/individual' + str(count) + '.abc'
        initial_abc_writer(title)
        count += 1

'''Current fitness function, just measures the distance of each note from note to note'''
def distance_fit(filename):
    #find the value of each note
    note_range = ['c', 'd', 'e', 'f', 'g', 'a', 'b', 'C', 'D', 'E', 'F',
             'G', 'A', 'B', 'c\'', 'd\'', 'e\'', 'f\'', 'g\'', 'a\'', 'b\'']
    #print('ind: ', filename)
    #file = filename
    #indfile = open(filepath + filename, 'r')
    
    if filename[0] == 'i':
        indfile = open(filepath + filename, 'r')
    else:
        path = filepath + filename[0]
        #print('filename for writer: ', path)
        indfile = open(path, 'r')
    '''
    global needs_first_tuple
    if needs_first_tuple == True:
        path = filepath + filename[0]
        print('filename for writer: ', path)
        indfile = open(path, 'r')
    else:
        indfile = open(filepath + filename, 'r')
    '''
    #ind_file = filepath + filename
    #print('ind_file: ', ind_file)

    #indfile = open(ind_file, 'r')
    content = indfile.readlines()
    items = content[7]

    notes = []
    note_values = []

    for item in items:
        if item in note_range:
            notes.append(item)
            note_values.append(note_range.index(item))

    '''find the distance between each note and the note after it'''
    distance = 0
    i = 0

    while i < len(note_values) - 1:
        distance += abs(note_values[i] - note_values[i+1])
        i += 1

    distance += abs(note_values[len(note_values) - 1])

    return distance

'''sorts the fitness of all the files from best to worst. used in selection'''
def sort_by_fitness(list_of_files):
    ind_fit = []
    i = 0
    new_list = []

    #print('file list: ', list_of_files)
    #remove old fitnesses for re-evaluation
    #new_list = [x[0] for x in list_of_files]
    #print(new_list)
    
    '''if file[1] = 0, then do current.
    if not, then do the first of the tuple'''
    for ind in list_of_files:
        fitness = distance_fit(ind)
        complete_ind = ind, fitness
        ind_fit.append(complete_ind)
        '''
        if len(ind[0]) == 3:
            ind = ind[0][0]
            #print('ind in fitness: ', ind)
            fitness = distance_fit(ind)
            complete_ind = ind, fitness
            ind_fit.append(complete_ind)
        else:
            #print('ind in fitness: ', ind)
            fitness = distance_fit(ind)
            complete_ind = ind, fitness
            ind_fit.append(complete_ind)
            '''
    '''
    global is_random
    global needs_first_tuple
    if is_random == False:
        for file, fitness in list_of_files:
            fit_tup = file, distance_fit(file)
            ind_fit.append(fit_tup)
            needs_first_tuple = True
            
    else:
        for file in list_of_files:
            fit_tup = file, distance_fit(file)
            print('fit_tup: ', fit_tup)
            ind_fit.append(fit_tup)
            is_random = False
    '''

    ind_fit = sorted(ind_fit, key=lambda ind_fit: ind_fit[1])

    return ind_fit

'''helper function to easily open files'''
def open_file(filename):
    opened_file = open(filepath + filename, 'r')
    return opened_file

'''two point crossover, may be too aggressive for this field'''
def two_point(ind1, ind2, child_files):
    if len(child_files) > 0:
        #print('ind1: ', ind1[0])
        #print('length: ', len(ind1))
        filepath1 = ind1
        filepath2 = ind2

        '''
        if len(ind1) == 2:
            filepath1 = ind1[0]
            filepath2 = ind2[0]
        else:
            filepath1 = ind1
            filepath2 = ind2
        '''
        #print('individual check', filepath1)

        #read both individual files
        ind1 = open_file(filepath1)
        ind2 = open_file(filepath2)


        #read in the line of note values for each individual
        content1 = ind1.readlines()
        notes1 = content1[7]

        content2 = ind2.readlines()
        notes2 = content2[7]

        #split both pieces into measures
        notes1 = notes1.split(" | ")
        notes2 = notes2.split(" | ")

        offspr = []
        note_num = 0

        #performs the crossover operation by going through each note and performing a 2 point crossover
        while note_num < len(notes1):
            if note_num < 3:
                offspr.append(notes1[note_num])
            elif note_num > 2 & note_num < 6:
                offspr.append(notes2[note_num])
            else:
                offspr.append(notes1[note_num])
            note_num += 1

        #print('offspring: ', offspr)
        #write to the correct file, one of the unused child files.
        
        filename = child_files[-1]
        child_files.pop()
        
        if len(filename) == 2:
            filename = filename[0]

        #print('filename: ', filename)

        abc_writer(filename, offspr)
        

    return filename, child_files

'''future mutation operator'''
def mutation(list_of_files, mut_prob, gene_prob):

    note_range = ['c', 'd', 'e', 'f', 'g', 'a', 'b', 'C', 'D', 'E', 'F',
                  'G', 'A', 'B', 'c\'', 'd\'', 'e\'', 'f\'', 'g\'', 'a\'', 'b\'']
    
    i = 0
    probs_ind = []
    while i < len(list_of_files):
        rand_mut = random.uniform(0, 1)
        probs_ind.append(rand_mut)

    probs_note = []
    while n < 100:
        rand_mut = random.uniform(0,1)
        probs_note.append(rand_mut)

    
    piece = 0
    for filename in list_of_files:
        if probs_ind[piece] <= mut_prob:
            new_music = []
            individual = open_file(filename)
            content = individual.readlines()
            music = content[7]
            measures = music.split(' | ')
            for measure in measures:
                new_measure = []
                notes = measure.split()
                new_notes = ''
                n = 0
                values = notes in note_range
                while n < len(notes):
                    if (notes[n] in note_range) and (probs_note[n] <= gene_prob):
                        up_down = random.randrange(-1,1)
                        new = note_range.index(notes[n])
                        new_notes += note_range[new + up_down]
                    else:
                        new_notes += notes[n]
                new_measure.append(new_notes)
        abc_writer(filename, new_music)
    return list_of_files
                
'''mu comma lambda selection. also runs the operator methods. this should be more user friendly and easier to change operators.'''
def mu_comma_lambda(files, mu, lbda, xo, mut):

    #sort the files by fitness in order to get mu parents
    ranked = sort_by_fitness(files)
    #save the best mu in a list
    best_ind = []
    i = 0
    while i < mu:
      best_ind.append(ranked[i][0])
      i += 1

    lbda_children = []
    new_pop = []
    n= 0
    list_counter = 1

    children = files 

    if len(children[0]) == 2:
        children = [x[0] for x in children]

    #find the top mu parents out of the ranked by fitness files. 
    #takes the top 5 individuals and creates a list as long as will be needed for crossover
    while n < lbda:
        #if the length of the list is less than the number of parents minus one, increase the counter
        if list_counter < mu - 1:
            file1 = best_ind[list_counter]
            file2 = best_ind[list_counter + 1]
            list_counter += 1
        #if on the last index of the best individuals, then start from the top of the list
        else:
            list_counter = 0
            file1 = best_ind[list_counter]
            file2 = best_ind[list_counter + 1]
            list_counter += 1
        
        #use the crossover operator
        if xo == 'two_point':
            offspring, children = two_point(file1, file2, children)
            lbda_children.append(offspring)
        
        #use the mutation operator
        if mut == 'mutation':
            lbda_children = mutation(children, 0.5, 0.5)

        #assign fitness to new offspring
        
        for ind in lbda_children:
            #print('ind: ', ind)
            fitness = distance_fit(ind)
            complete_ind = ind, fitness
            new_pop.append(complete_ind)
            '''
            if len(ind[0]) == 3:
                ind = ind[0][0]
                #print('ind in fitness: ', ind)
                fitness = distance_fit(ind)
                complete_ind = ind, fitness
                new_pop.append(complete_ind)
            else:
                #print('ind in fitness: ', ind)
                fitness = distance_fit(ind)
                complete_ind = ind, fitness
                new_pop.append(complete_ind)
            '''
        n+=1
        #print('n: ', n)

    return new_pop

def print_statistics(population, gen):
    best_individual = ''
    best_fitness = 1000
    worst_fitness = 0
    worst_individual = ''
    all_fitnesses = []

    for individual, fitness in population:
        if fitness < best_fitness:
            best_individual = individual
            best_fitness = fitness
        if fitness > worst_fitness:
            worst_individual = individual
            worst_fitness = fitness
        all_fitnesses.append(fitness)

    average_fitness = sum(all_fitnesses)/len(all_fitnesses)

    statistics = f'{gen}\t{best_individual}, {best_fitness}\t{average_fitness}\t{worst_individual}, {worst_fitness}\t'
    print(statistics)

def main():
    pop_initialization(21)

    num_gens = 4
    gen_counter = 1

    #save filepath and list of all files in it
    list_of_files = []

    for file in os.listdir(filepath):
        list_of_files.append(file)

    new_pop = list_of_files
    
    print('gen\tbest individual\taverage fitness\tworst individual')
    #repeat for each generation
    while gen_counter <= num_gens:

        #send list of files to mu_comma_lambda for evaluation
        new_pop = mu_comma_lambda(new_pop, 3, 21, 'two', 'mutation')
        print('gen number:' , gen_counter)
        print_statistics(new_pop, gen_counter)

        gen_counter += 1
        
if __name__ == '__main__':

    #saves the current version of code and output for the records.
    now = datetime.now()
    src = '/Users/lizyhoepfinger/Desktop/ECFinal/musicga.py'
    dest = '/Users/lizyhoepfinger/Desktop/ECFinal/runs/' + now.strftime("%m_%d_%H%M") + '.txt'
    code_save = '/Users/lizyhoepfinger/Desktop/ECFinal/runs/CODE' + now.strftime("%m_%d_%H%M") + '.txt'
    
    sys.stdout = open(dest, 'w')
    shutil.copy(src, code_save)
    main()
    
   
    
    


        