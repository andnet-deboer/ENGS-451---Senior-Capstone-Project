# Import necessary libraries
from music21 import *
import time

# Convert the file to a stream
parsed_work = converter.parse('Two-bar C major scale.xml')

# Depth-first search traversal
recurse_work = parsed_work.recurse()

# Create a list to store the notes in chronological order
notes_in_chronological_order = []

# Iterate through all note objects in the score and add them to the list
for element in recurse_work.notes:
    notes_in_chronological_order.append(element)

# Sort the notes by their start times
notes_in_chronological_order.sort(key=lambda note: note.offset)

parsed_work.plot()
# Iterate through the sorted notes and play them at their respective start times
for element in notes_in_chronological_order:
    time.sleep(element.offset)
    print(element.name)
    #element.show('midi')
    print("Servo moving now")

    
