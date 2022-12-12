import random
import os
import sys
import shutil
import numpy as np

from itertools import cycle
from music21 import converter
from datetime import datetime
from itertools import chain

'''
declaring global variables that are used throughout methods. 
these include population initialization, headers of the files, and filenames
'''
filepath = 'individuals/'
note_lengths = ['1', '2', '3', '4']
lengths = [1, 2, 2, 2, 2, 3, 3, 3, 4]
note_range = ['g', 'a', 'b', 'C', 'D', 'E', 'F',
              'G', 'A', 'B', 'c\'', 'd\'', 'e\'', 'f\'', 'g\'']
letters = ['c', 'd', 'e', 'f']
tonic = ['g', 'a', 'b', 'C', 'D', 'E',
         'F', 'G', 'A', 'B', 'c\'', 'd\'', 'e\'', 'f\'', 'g\'']
major_chord = ['g', 'C', 'E', 'G', 'c\'', 'e\'']
inner_range = note_range[12:24]
harm_same_a = []
harm_same_b = []

accidentals = ['^', '_']
t = 'T:' + 'title' + '\n'
x = 'X:' + '1' + '\n'
k = 'K:' + 'C' + '\n'
m = 'M:' + '4/4' + '\n'
l = 'L:1/8\n'
r = 'R:' + 'Reel' + '\n'
q = 'Q:' + '100' + '\n'

header = x + t + m + q + l + r + k


'''
Creates the initial population of random abc individuals. 
This method randomly adds appropriate notes to the individuals.
This includes the headers of the abc files as well.
'''


def initial_abc_writer(filename):
    file_contents = header

    #starting with the first measure, write music. this is truly random. individuals will be saved in a .abc file
    music = ''
    measures = 0

    while measures < 8:
        beats = 0

        if measures == 0:
            music += 'C2'
            beats += 2

        while beats < 8:

            music += str(random.choice(note_range))
            note_value = random.choice(lengths)

            if (8-beats) < note_value:
                note_value = 1

            beats += note_value

            if note_value != 1:
                music += str(note_value)

        music += ' | '
        measures += 1

    file_contents += music
    #print(f'initialized music: {music}')
    abcfile = open(filename, 'w')
    abcfile.write(file_contents)
    abcfile.close()


'''
Writes the offspring to files overriding previous generation's files. 
This method also implements the header as well as the generated indivuals.
It takes in the filename and the generated notes and writes them to a file.
'''


def abc_writer(filename, notes):

    measure = 0
    #print(f'filename: {filename}, filepath: {filepath}')
    offspring = open(filepath + filename, 'w')
    offspring.write(header)
    #print(f'notes: {notes}')
    while measure < len(notes):
        if measure == len(notes) - 1:
            offspring.write(notes[measure])
        else:
            offspring.write(notes[measure] + ' | ')
        measure += 1

    offspring.close()


def get_music(file):
    opened = open_file(file)
    content = opened.readlines()
    music = content[7]
    return music


def repair(measure):
    beats = 0
    note_beat = 0
    #measure = note_list(measure)
    #measure = [i for i in measure if i]
    #print(f'measure before repair: {measure}')

    i = 0
    while i < len(measure):
        #print(f'measure i: {measure[i]}')

        if measure[i] in note_lengths:
            beats += int(measure[i])
            note_beat += 1
            i += 1
            
        elif measure[i] in note_range:
            beats += 1
            i += 1
            
        elif measure[i] in letters:
            beats += 1
            i += 1

        else:
            i += 1

    beats = beats - note_beat
    #print(f'number of beats: {beats}')

    while beats < 8:
        #print(f'not enough, adding more')
        measure += random.choice(note_range)
        beats += 1

    new_meas = ''
    b2 = 0
    nb = 0
    i = 0
    while beats > 8:
        #print('too many, should be going down')
        if measure[-1] in note_lengths:
            beats -= int(measure[-1])
            beats += 1
            measure = measure.rstrip(measure[-1])
        elif measure[-1] in note_range or measure[-1] in letters:
            beats -= 1
            measure = measure.rstrip(measure[-1])
        else:
            measure = measure.rstrip(measure[-1])
            
    measure = measure.replace('\'\'', '\'')


    #print(f'measure after repair: {measure}')
    return measure


'''
This function implements a tournament selection to choose the new parents.
It takes in the population, the desired tournament size, and the number of parents being chosen
returns a list of parents (just filenames that contain the individual)
'''


def tournament(population, tourn_size, mu):
    parents = []

    for x in range(mu):
        selected = []
        best = ''
        #generate tournsize number of random individuals from the population
        for i in range(tourn_size):
            selected.append(random.choice(population))
        #choose the best individual in the tournament
        selected = sorted(selected, key=lambda selected: selected[1])
        #add best to the list of parents
        parents.append(selected)

    parents = [p[0] for p in parents]
    #print(f'parents: {parents}')
    return parents


'''
randomly initializes a population
uses initial_abc_writer(). takes in the desired population size
'''


def pop_initialization(num_of_individuals):
    count = 1
    file_list = []
    while count <= num_of_individuals:
        title = 'individual' + str(count) + '.abc'
        initial_abc_writer(filepath + title)
        file_list.append(title)
        count += 1

    return file_list


def check_oct(note, oct):
    if oct == '\'':
        note += oct

    return note


def adap_fit(filename):
    music = get_music(filename)
    penalty = 0
    music = music.split(' | ')
    #print(f'music: {music}')

    '''
    A best note will be in both the inner range of notes (the middle octave) and the tonic scale.
    Because each peice of music contains a different number of notes, the penalty achieved will be divided by the 
    length of the notes in the piece (or the maximum penalty that can be achieved.) and the fitness will be based on that 
    percentage score.'''

    best_notes = 0
    total_notes = 0
    prev_note = note_range.index('C')
    distance = 0
    for measure in music:
        #print(f'measure: {measure}')
        notes = note_list(measure)
        notes = [i for i in notes if i]
        
        #print(f'notes: {notes} in {filename}')
        for note in notes:
            note = note.replace('\'\'', '\'')

            if note in letters:
                note += '\''

            if note in tonic:
                penalty += -1
            else:
                penalty += 1

            if note in inner_range:
                penalty += -3
            else:
                penalty += 3

            if note in major_chord:
                penalty += -2
            else:
                penalty += 2

            if note not in note_lengths:
                note_index = note_range.index(note)
                distance += abs(prev_note - note_index)
                prev_note = note_range.index(note)

            total_notes += 1

    if note_range[prev_note] == 'C':
        penalty += -2

    #penalty = (penalty/(total_notes*6))*100
    fitness = (distance + penalty)/total_notes


    #print(f'total notes in {filename}: {total_notes}')

    return fitness


'''
helper function that takes a string of notes and returns a list that has each note value as its own item.
'''


def note_list(items):
    #print(f'items: {items}')
    #replace ' with o for easier comprehension
    items = repair(items)
    #print(f'repaired items: {items}')
    items = items.replace('\'', 'o')
    items = [*items]

    #print(f'items: {items}')
    letters = ['c', 'd', 'e', 'f']

    '''save each note as an item in a list.
    iterate through the list, and for each value, save the distance in another list.
    '''
    note = ''
    notes = []
    i = 0

    while i < len(items):
        if items[i] in note_range and items[i-1] not in accidentals:
            notes.append(note)
            note = ''
            note += items[i]
            i += 1
            continue
        if items[i] == 'o':
            note += '\''
            notes.append(note)
            note = ''
            #print(f'item i 3: {items[i]}')
            i += 1
            continue
        if items[i] in note_range:
            notes.append(items[i])
            note = ''
            note += items[i]
            i += 1
            #print(f'item i 4: {items[i]}')
            continue
        if items[i] in note_lengths:
            notes.append(note)
            notes.append(items[i])
            note = ''
            #print(f'item i 5: {items[i]}')
            i += 1
            continue
        if items[i] in letters:
            notes.append(items[i])
            note =''
            note += items[i] + '\''
            #print(f'item i 6: {items[i]}')
            i += 2
        else:
            notes += items[i]
            notes.append(items[i])
            note = ''
            i += 1
        
    #notes = repair(notes)
    #print(f'listed: {notes}')
    return notes


'''
sorts the fitness of all the files from best to worst. used in selection.
Takes in a list of filenames and returns a list of tuples that contain the filename and 
its fitness in a ranked list.
'''


def sort_by_fitness(list_of_files):
    ind_fit = []

    for ind in list_of_files:
        fitness = adap_fit(ind)
        complete_ind = ind, fitness
        ind_fit.append(complete_ind)

    ind_fit = sorted(ind_fit, key=lambda ind_fit: ind_fit[1])
    #ind_fit.sort(key = lambda x: x[1])
    #print(ind_fit)

    return ind_fit


'''
helper function to count the number of beats in a measure. 
this checks to be sure we have accurate representations
'''


def beat_counter(measure):
    beats = 0
    for value in measure:
        if value in note_lengths:
            beats += int(value)
        elif value in note_range:
            beats += 1
    return beats


'''
helper function to open a file
'''


def open_file(filename):
    opened_file = open(filepath + filename, 'r')
    return opened_file


'''
mutation helper function. 
takes in the filename, a list of measures, and the probability that a gene will be mutated.
'''


def creep(filename, measures, gene_prob):
    #print('filename: ', filename)
    n = 0
    change = []
    rand_mut = [random.uniform(0, 1) for _ in range(100)]

    if len(measures) > 8:
        measures = measures.pop()

    for prob in rand_mut:
        if prob < gene_prob:
            change.append(1)
        else:
            change.append(0)

    m = 0

    new_music = []
    low_edge = ['c', '^c', 'd', '^d']
    up_edge = ['^g\'', 'a\'', '_b\'', 'b\'']

    for measure in measures:
        #print(f'measure before mutation: {measure}')
        new_measure = ''
        #print(f'list of notes: {measure}')
        notes = note_list(measure)
        #print(f'notes: {notes}')
        ##print(f'notes list: {notes}')
        notes = [i for i in notes if i]
        acc = ''
        oct = ''

        for note in notes:

            #print(f' note: {note}')
            if note == "''" or note == '':
                continue
            if change[n] == 0:
                new_measure += note
                n += 1
                continue
            '''
            if note == '^':
                acc = '^'
                continue
            if note == '_':
                acc = '_'
                continue
            if note == '\'':
                oct = '\''
                continue
            '''
            if note in note_lengths:
                new_measure += note
            else:
                note_value = acc + note + oct
                if note_value not in note_range:
                    note_value = random.choice(note_range)
                index = note_range.index(note_value)
                if index > len(note_range)-2:
                    new_measure += note_range[index - 1]
                elif index < 2:
                    new_measure += note_range[index + 1]
                else:
                    #print(f'index: {index}')
                    new_measure += note_range[index + random.choice([-1, 1])]
            
            n += 1
        #print(f'new music after mutation: {new_measure}')
        #new_measure = [new_measure]
        #print(f'new measure before repair: {new_measure}')

        new_measure = repair(new_measure)
        #print(f'repaired measure {new_measure}')

        new_music.append(new_measure)

        #print(f'new music: {new_music}')

        #new_music.append(' | ')

    #print('new_music: ', new_music)
    abc_writer(filename, new_music)


'''
creep mutation method: works by chosing sinlge notes from an individual 
and either increasing or decreasing random notes within the file according to a predefined probability
'''


def creep_mutation(individuals, mut_prob, gene_prob):
    offspring = []
    for ind in individuals:
        probs_ind = random.uniform(0, 1)
        if probs_ind <= mut_prob:
            music = get_music(ind)
            measures = music.split(' | ')
            if len(measures) > 8:
                measures.pop()
            #print(f'pre mutated measures: {measures}')
            creep(ind, measures, gene_prob)
        else:
            continue


'''crossover operator: similar to binary uniform crossover- measures are randomly chosen from each parent
to generate an offspring'''


def uniform_crossover(individuals):
    ind = 0
    while ind < len(individuals):

        file1 = individuals[ind]
        file2 = individuals[ind-1]

        music1 = get_music(file1)
        music2 = get_music(file2)

        #swaps random measures between parents to create a child
        measures1 = music1.split(' | ')
        measures2 = music2.split(' | ')

        #print(f'measures1: {measures1}')
        #print(f'measures2: {measures2}')

        probs = []
        i = 0
        while i < len(measures1):
            probs.append(random.choice([0, 1]))
            i += 1

        offspringm = []
        index = 0
        for m1, m2 in zip(measures1, measures2):
            if probs[index] == 0:
                offspringm.append(m1)
            else:
                offspringm.append(m2)
            index += 1

        for m in offspringm:
            m = repair(m)

        #print(f'new music offspring: {offspringm}')
        abc_writer(individuals[ind], offspringm)

        ind += 1


'''
the evolutionary algorithm: given a population size, will run an ea according to what the user defines.
'''


def ea(pop_size, individuals, mu, operators, tourn_size):

    #new_pop = [x[0] for x in new_pop]
    #ranked = sort_by_fitness(individuals)
    #print(f'ranked fitnesses: {ranked}')
    #ranked = [x[0] for x in ranked]
    #best_parents = ranked[:num_best]
    #print(f'new parents: {best_parents}')

    parents = tournament(individuals, tourn_size, mu)
    #print(f'parents: {parents}')
    #parents = [p[0] for p in parents]
    #print(f'parents: {parents}')
    #parents = []
    num_offspring = 0
    if len(parents[0]) == 2:
        for i in range(pop_size):
            parents.append(random.choice(parents))
        parents = [p[0] for p in parents]
    else:
        for i in range(pop_size):
            parents.append(random.choice(parents))

    offspring = parents
    #print(f'offspring: {offspring}')
    #offspring = [o[0] for o in offspring]
    #print('crossover')
    if 'uniform_crossover' in operators:
        uniform_crossover(offspring)
    #print('mutation')
    if 'creep_mutation' in operators:
        creep_mutation(individuals, 0.5, 0.3)

    #evaled_ind = sort_by_fitness(individuals)

    #determine fitness for each value
    evaled_ind = []
    for individual in individuals:
        fitness = adap_fit(individual)
        ind_tup = individual, fitness
        evaled_ind.append(ind_tup)
    #print(f'fitness: {evaled_ind}')

    return evaled_ind


'''
helper function that prints out statistics of each run
'''


def print_statistics(population, gen, best_ind):
    best_individual = ''
    best_fitness = 10000
    worst_fitness = 0
    worst_individual = ''
    all_fitnesses = []

    file, best_fit = best_ind

    previous_ind = 1000
    for individual, fitness in population:
        if fitness < previous_ind:
            previous_ind = fitness
            best_individual = individual
            best_fitness = fitness
        if fitness > worst_fitness:
            worst_individual = individual
            worst_fitness = fitness
        if fitness < best_fit:
            best_ind = individual, fitness
            shutil.copy(filepath+individual,
                        '/Users/lizyhoepfinger/Desktop/ECFinal/best_ind.abc')
        all_fitnesses.append(fitness)

    average_fitness = sum(all_fitnesses)/len(all_fitnesses)

    statistics = f'{gen}\t{best_individual}, {best_fitness}\t\t{average_fitness}\t\t{worst_individual}, {worst_fitness}\t'
    print(statistics)

    return best_ind


def main():
    pop_size = 100
    list_of_files = pop_initialization(pop_size)

    num_gens = 300
    gen_counter = 1
    lbda = pop_size
    mu = int(pop_size/7)
    file = ''
    best_fitness = 1000
    best_ind = file, best_fitness
    new_pop = list_of_files

    print('gen\tbest individual\t\t\taverage fitness\t\tworst individual')
    #repeat for each generation
    while gen_counter <= num_gens:

        #send list of files to mu_comma_lambda for evaluation
        new_pop = ea(pop_size, new_pop, mu, [
                     'uniform_crossover', 'creep_mutation'], tourn_size=30)
        #print('gen number:' , gen_counter)
        best_ind = print_statistics(new_pop, gen_counter, best_ind)

        new_pop = [n[0] for n in new_pop]
        #drop tuple of fitness so the only list values are filenames
        #new_pop = [x[0] for x in new_pop]
        gen_counter += 1


if __name__ == '__main__':

    #saves the current version of code and output for the records.
    now = datetime.now()
    src = '/Users/lizyhoepfinger/Desktop/ECFinal/musicea.py'
    dest = '/Users/lizyhoepfinger/Desktop/ECFinal/runs/EA' + \
        now.strftime("%m_%d_%H%M") + '.txt'
    code_save = '/Users/lizyhoepfinger/Desktop/ECFinal/runs/CODE' + \
        now.strftime("%m_%d_%H%M") + '.txt'

    sys.stdout = open(dest, 'w')
    print('file run: musicea.py')
    shutil.copy(src, code_save)
    main()
    s = converter.parse('best_ind.abc')
    best = s.write('midi', '/Users/lizyhoepfinger/Desktop/ECFinal/best_ind.mid')
#s.show('midi')
   
