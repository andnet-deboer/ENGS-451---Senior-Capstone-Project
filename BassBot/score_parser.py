import csv
import xml.etree.ElementTree as ET
from datetime import timedelta
from music21 import converter, tempo, meter, note, chord
import os


class ScoreParser:
    def __init__(self, music_file, bpm_override=None, use_file_bpm=True):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        songs_dir = os.path.join(base_dir, "Songs")
        self.music_file = os.path.join(songs_dir, music_file)
        self.parsed_work = converter.parse(self.music_file)
        self.time_signature = self._get_time_signature()
        self.bpm = self._determine_bpm(bpm_override, use_file_bpm)
        self.time_per_quarter = 60 / self.bpm * self.time_signature.beatDuration.quarterLength
        self.note_matrix = []

    def _get_time_signature(self):
        ts = self.parsed_work.recurse().getElementsByClass(meter.TimeSignature).first()
        if ts is None:
            print("[ScoreParser] No time signature found. Using default 4/4.")
            return meter.TimeSignature('4/4')
        return ts

    def _get_bpm_from_musicxml(self):
        try:
            tree = ET.parse(self.music_file)
            root = tree.getroot()
            for sound in root.iter('sound'):
                if 'tempo' in sound.attrib:
                    return float(sound.attrib['tempo'])
        except Exception as e:
            print(f"[ScoreParser] Error parsing XML directly: {e}")
        return None

    def _get_bpm_from_directions(self):
        for direction in self.parsed_work.recurse().getElementsByClass('Direction'):
            if hasattr(direction, 'xmlElement') and direction.xmlElement is not None:
                for elem in direction.xmlElement.iter():
                    if elem.tag.endswith('sound') and 'tempo' in elem.attrib:
                        try:
                            return float(elem.attrib['tempo'])
                        except ValueError:
                            continue

        bpm_mark = self.parsed_work.recurse().getElementsByClass(tempo.MetronomeMark).first()
        if bpm_mark and bpm_mark.number:
            return bpm_mark.number

        return self._get_bpm_from_musicxml()

    def _determine_bpm(self, override, use_file):
        if override is not None:
            return override
        if use_file:
            bpm = self._get_bpm_from_directions()
            if bpm is not None:
                return bpm
        return 120  # fallback default
    def generate_note_matrix(self, octave_adjustment=0):
        self.note_matrix = []
        track_time = 0.0

        for element in self.parsed_work.recurse():
            if hasattr(element, 'octave') and octave_adjustment != 0:
                element.octave += octave_adjustment
            if not isinstance(element, (note.Note, note.Rest)):
                continue

            duration = element.duration.quarterLength * self.time_per_quarter
            start = timedelta(seconds=track_time)
            track_time += duration
            end = timedelta(seconds=track_time)

            if isinstance(element, note.Note):
                label = element.nameWithOctave
                type_ = "Note"
            else:
                label = "Rest"
                type_ = "Rest"

            row = [element, type_, label, str(start), str(end), round(duration, 3)]
            self.note_matrix.append(row)

        return self.note_matrix

    def save_note_matrix(self, filename):
        if not self.note_matrix:
            self.generate_note_matrix()

        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Element Object", "Element Type", "Pitch/Rest", "Start Time", "End Time", "Duration (sec)"])
            writer.writerows(self.note_matrix)
        print(f"[ScoreParser] Saved timing info to: {filename}")
