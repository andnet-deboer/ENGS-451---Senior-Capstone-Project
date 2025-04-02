from bass import Bass


class Composer:

    

    def play_notes(note_matrix):
        for i in range(len(note_matrix) - 1):  # Iterate up to the second-to-last row
                    current_row = note_matrix[i]
                    next_row = note_matrix[i + 1]  # Access the next row

                    note = current_row[0]
                    if note.isNote:
                        octave = current_row[0].octave+1
                    else:
                        octave = 0
                
                    current_time = current_row[2]
                    next_time = next_row[2]  # Access a value from the next row
                    duration = current_row[4]

                    if note.isNote:
                        #All non open string notes
                        if note_mapping[note.name,octave][1] is not None:
                            relay_off(note_mapping[note.name,octave][1])  # Unfret all other frets
                            #damper.on()  # Fret the note
                            #time.sleep(0.2)
                            note_mapping[note.name,octave][1].on()  # Fret the note
                            #damper.off()  # UnFret the note
                            note_mapping[note.name,octave][0].pick()  # Pick the note
                        #Open string notes
                        elif note_mapping[note.name,octave][1] is None:
                            lib8relind.set_all(0, 0) #Turn off all frets
                            note_mapping[note.name,octave][0].pick()  # Pick the note
                        time.sleep(duration)
                        #damper.off()
                    else:
                        #damper.off()
                        time.sleep(duration)
                        lib8relind.set_all(0, 0)#Turn off all frets
                    