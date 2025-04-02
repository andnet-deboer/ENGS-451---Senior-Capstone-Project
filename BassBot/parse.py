import csv
from datetime import timedelta
from music21 import converter, tempo, meter, note, chord
import xml.etree.ElementTree as ET

class Parse:
    @staticmethod
    def get_bpm_from_musicxml(musicFile):
        try:
            tree = ET.parse(musicFile)
            root = tree.getroot()
            for sound in root.iter('sound'):
                if 'tempo' in sound.attrib:
                    return float(sound.attrib['tempo'])
        except Exception as e:
            print("Error parsing XML directly:", e)
        return None

    @staticmethod
    def get_bpm(parsed_work, musicFile=None):
        for direction in parsed_work.recurse().getElementsByClass('Direction'):
            if hasattr(direction, 'xmlElement') and direction.xmlElement is not None:
                for elem in direction.xmlElement.iter():
                    if elem.tag.endswith('sound') and 'tempo' in elem.attrib:
                        try:
                            return float(elem.attrib['tempo'])
                        except ValueError:
                            continue

        bpm_mark = parsed_work.recurse().getElementsByClass(tempo.MetronomeMark).first()
        if bpm_mark and bpm_mark.number:
            return bpm_mark.number

        if musicFile:
            bpm_from_xml = Parse.get_bpm_from_musicxml(musicFile)
            if bpm_from_xml is not None:
                return bpm_from_xml

        return 120  # default fallback

    @staticmethod
    def generate_note_matrix(musicFile, bpm=None, use_file_bpm=True):
        parsed_work = converter.parse(musicFile)

        # Get time signature
        ts = parsed_work.recurse().getElementsByClass(meter.TimeSignature).first()
        if ts is None:
            print("No time signature found. Using default 4/4.")
            ts = meter.TimeSignature('4/4')
        print("Time Signature:", ts.ratioString)

        # Determine BPM
        if bpm is None and use_file_bpm:
            bpm = Parse.get_bpm(parsed_work, musicFile)
        elif bpm is None:
            bpm = 120  # default fallback

        print("Using BPM:", bpm)

        timePerQuarter = 60 / bpm * ts.beatDuration.quarterLength
        trackTime = 0.0
        note_matrix = []

        # Filter only Note and Rest (skip Chords and others)
        for element in parsed_work.recurse():
            if isinstance(element, chord.Chord):
                continue  # skip chords
            if not isinstance(element, (note.Note, note.Rest)):
                continue  # skip everything else

            duration = element.duration.quarterLength * timePerQuarter
            start_time = timedelta(seconds=trackTime)
            trackTime += duration
            end_time = timedelta(seconds=trackTime)

            if isinstance(element, note.Note):
                label = f"{element.nameWithOctave}"
                element_type = "Note"
            elif isinstance(element, note.Rest):
                label = "Rest"
                element_type = "Rest"

            row = [element_type, label, str(start_time), str(end_time), round(duration, 3)]
            note_matrix.append(row)

        return note_matrix

    @staticmethod
    def save_note_matrix(musicFile, filename, bpm=None, use_file_bpm=True):
        note_matrix = Parse.generate_note_matrix(musicFile, bpm, use_file_bpm)

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Element Type", "Pitch/Rest", "Start Time", "End Time", "Duration (sec)"])
            writer.writerows(note_matrix)

        print(f"Saved timing info to: {filename}")
        return note_matrix

Parse.save_note_matrix("VivaLaVida.xml", "VivaLaVida.csv", use_file_bpm=True)