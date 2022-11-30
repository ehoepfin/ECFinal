import random
import os
import numpy as np

from itertools import cycle
from music21 import converter

'''initialize population'''

'''Initializes the header for the population. the population has the same metadata, style, key, meter, and speed.
returns the first 7 lines of the abc file needed for creation of the file.'''
def abcheader(title, number, key, meter, style, speed):
  header = ''
  t = 'T:' + str(title) + '\n'
  x = 'X:' + str(number) + '\n'
  k = 'K:' + str(key) + '\n'
  m = 'M:' + str(meter) + '\n'
  l = 'L:1/8\n'
  r = 'R:' + str(style) + '\n'
  q = 'Q:' + str(speed) + '\n'

  header += x + t + m + q + l + r + k
  return header

'''creates the music. adds random notes to the file with no specific length or accidental value.
returns the file contents, which is the actual music.'''
def abcmusic(header):
  middle_octave = ['c', 'd', 'e', 'f', 'g', 'h', 'a', 'b']
  low_octave = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
  upper_octave = ['c\'', 'd\'', 'e\'', 'f\'', 'g\'', 'h\'', 'a\'', 'b\'']

  range = ['c', 'd', 'e', 'f', 'g', 'a', 'b', 'C', 'D', 'E', 'F', 'G', 'A', 'B', 'c\'', 'd\'', 'e\'', 'f\'', 'g\'', 'a\'', 'b\'']

  accidentals = ['^', '_']

  #starting with the first measure, write music. this is truly random. individuals will be saved in a .abc file
  music = ''
  measures = 0

  while measures < 8:
    
    beats = 0
    while beats < 8:
      
      acc_prob = random.randint(1, 20)

      if (acc_prob >= 19):
        music += ' ' + accidentals[random.randint(0, 1)]
        
      music += str(random.choice(range))
      value = random.randint(1, 4)
      


      if (8-beats) < value:
        value = 1

      beats += value

      if value != 1:
        music += str(value)
          
    music += ' | '
    measures += 1

  file_contents = header + music
  return file_contents

'''writes the contents to the file. the file is the individual. all of these are initially random,
this uses the helper functions to add the contents to the abc file'''
def write_abc(filename):
    header = abcheader('title', '1', 'C', '4/4', 'Reel', '120')
    generated_music = abcmusic(header)
    
    file = open(filename, 'w')
    file.write(generated_music)
    file.close()

'''initializes the population. uses the write_abc function create a set number of files/individuals'''
def pop_initialization(num_of_individuals):
    count = 1

    while count <= num_of_individuals:
        title = 'individuals/individual' + str(count) + '.abc'
        write_abc(title)
        count += 1

'''used as part of the fitness function for now. finds the index of each note in the abc file and saves that in a separate 
list to be used in the fitness function'''
def find_note_values(file):
  range = ['c', 'd', 'e', 'f', 'g', 'a', 'b', 'C', 'D', 'E', 'F',
             'G', 'A', 'B', 'c\'', 'd\'', 'e\'', 'f\'', 'g\'', 'a\'', 'b\'']

  filepath = 'individuals/'
  indfile = open(filepath + file, 'r')
  content = indfile.readlines()
  items = content[7]

  notes = []
  note_values = []

  for item in items:
    if item in range:
      notes.append(item)
      note_values.append(range.index(item))

  return notes, note_values

def fitness(individual):
  notes, note_values = find_note_values(individual)

  '''find the distance between each note and the note after it'''
  distance = 0
  i = 0

  while i < len(note_values) - 1:
    distance += abs(note_values[i] - note_values[i+1])
    i += 1

  distance += abs(note_values[len(note_values) - 1])

  return distance
  
def sort_by_fitness(list_of_files):
  ind_fit = []
  i = 0

  while i < len(list_of_files):
    ind_fit.append([list_of_files[i], fitness(list_of_files[i])])
    i += 1

  ind_fit = sorted(ind_fit, key=lambda ind_fit: ind_fit[1])

  #print(ind_fit)

  return ind_fit

def open_file(filename):
  opened_file = open(filename, 'r')
  return opened_file

'''crossover operators'''

'''2-point crossover. the user specifies how many points there should be'''
def n_point(ind1, ind2, child_files):
  filepath1 = 'individuals/' + ind1
  filepath2 = 'individuals/' + ind2

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
    if note_num > 2 & note_num < 6:
      offspr.append(notes2[note_num])
    else:
      offspr.append(notes1[note_num])
    note_num += 1

  #write to the correct file, one of the unused child files. 
  filename = child_files[-1]
  child_files.pop()
  offspring = open('individuals/' + filename, 'w')

  header = abcheader('title', '1', 'C', '4/4', 'Reel', '120')

  offspring.write(header)

  measure = 0
  while measure < len(offspr):
    offspring.write(offspr[measure] + ' | ')
    measure += 1

  offspring = filename

  return offspring, child_files

  
def mu_comma_lambda(best_ind, files, mu, lbda):
  
  lbda_children = []
  new_pop = []
  n = 0
  list_counter = 0

  children = [x for x in files if x not in best_ind]

  
  while n < lbda:
    if list_counter < mu-1:
      file1 = best_ind[list_counter]
      file2 = best_ind[list_counter + 1]
      list_counter += 1
    else:
      list_counter = 0
      file1 = best_ind[list_counter]
      file2 = best_ind[list_counter + 1]
      list_counter += 1

    offspring, children = n_point(file1, file2, children)
    

    lbda_children.append(offspring)
    n += 1

  lbda_children = sort_by_fitness(lbda_children)
    
  for ind in lbda_children[:lbda]:
    new_pop.append(ind)


  print("new Population: ", new_pop)

  return new_pop
    

def main():
  pop_initialization(20)

  num_gens = 10
  gen_counter = 1

  while gen_counter < num_gens:
    
    '''setting up for a fitness function. each note gets assigned a value correpsonding to its position in the initial list'''
    path = 'individuals/'
    list_of_files = []
    
    for file in os.listdir(path):
      list_of_files.append(file)

    ranked = sort_by_fitness(list_of_files)

    mu = 5
    lbda = 15
    best_ind = []
    i = 0
    while i < mu:
      best_ind.append(ranked[i][0])
      i += 1
  
    mu_comma_lambda(best_ind, list_of_files, mu, lbda)

    gen_counter += 1

  '''code to play an individual. On my mac it opens garageband, you may need to install some kind of midi player to listen'''
  #s = converter.parse('individuals/individual1.abc')
  #s.show('midi')

'''parent selection'''


'''crossover'''


'''mutation'''


'''fitness'''

if __name__ == '__main__':
  
  main()








    
