import random
import os
import numpy as np
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

      if (acc_prob <= 15):
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
def two_point(ind1, ind2):
  filepath1 = 'individuals/' + ind1
  filepath2 = 'individuals/' + ind2

  with open(filepath1, 'r') as f:
    print(f.read())

  with open(filepath2, 'r') as q:
    print(q.read())
  

  ind1 = open_file(filepath1)
  ind2 = open_file(filepath2)

  content1 = ind1.readlines()
  items1 = content1[7]

  content2 = ind2.readlines()
  items2 = content2[7]

  notes1 = items1.split(" | ")
  notes2 = items2.split(" | ")

  count = 0
  points = []
  while count < 2:
    point = random.randint(0,len(notes1)-2)
    if point not in points:
      points.append(point)
      count += 1

  offspring1notes = []
  offspring2notes = []
  switch = 0
  i = 0

  print("notes one: ", len(notes1))
  while i < (len(notes1)-1):
    if i in points:
      switch += 1
      offspring1notes.append(notes2[i])
      offspring2notes.append(notes1[i])
    if i not in points:
      if switch % 2 == 1:
        offspring1notes.append(notes1[i])
        offspring2notes.append(notes2[i])
      else:
        offspring1notes.append(notes2[i])
        offspring2notes.append(notes1[i])
    i += 1
  
  header = abcheader('title', '1', 'C', '4/4', 'Reel', '120')

  offspring1 = open(filepath1, 'w')
  offspring2 = open(filepath2, 'w')

  offspring1.write(header)
  offspring2.write(header)

  j = 0
  n = 0

  while j < len(offspring1notes):
    content = offspring1notes[j] + " | "
    offspring1.write(content)
    j += 1


  while n < len(offspring2notes):
    content = offspring2notes[n] + " | "
    offspring2.write(content)
    n += 1

  return offspring1, offspring2

#def mu_plus_lambda(ranked_files):
def main():
  pop_initialization(20)

  num_gens = 5
  gen_counter = 0

  while gen_counter < num_gens:
    
    
    '''setting up for a fitness function. each note gets assigned a value correpsonding to its position in the initial list'''
    path = 'individuals/'
    list_of_files = []

    for file in os.listdir(path):
      list_of_files.append(file)

    ranked = sort_by_fitness(list_of_files)
    print(ranked)

    i = 0
    while i < len(list_of_files):
      file1 = list_of_files[i]
      file2 = list_of_files[i+1]
      two_point(file1, file2)
      i += 2
    
    gen_counter += 1

  '''code to play an individual. On my mac it opens garageband, you may need to install some kind of midi player to listen'''
  s = converter.parse('individuals/individual1.abc')
  s.show('midi')

'''parent selection'''


'''crossover'''


'''mutation'''


'''fitness'''

if __name__ == '__main__':
  main()








    
