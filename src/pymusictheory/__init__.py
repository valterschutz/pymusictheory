"""
Vocabulary:
"semitone offset": The number of semitones away from the previous C. Always positive.
"absolute semitone offset": The number of semitones away from C0.
"semitone distance": A number of semitones.
"""
from enum import Enum
from functools import total_ordering
from hmac import new
import subprocess
from typing import Self


# Enum for musical note letters
class NoteLetter(Enum):
    """
    Enum representing musical note letters.
    """

    C = 0
    D = 1
    E = 2
    F = 3
    G = 4
    A = 5
    B = 6

    def __str__(self) -> str:
        return self.name

    def __add__(self, other: int) -> "NoteLetter":
        """
        When adding letters, treat them as integers and wrap around if necessary.
        """
        new_value = (self.value + other) % len(NoteLetter)
        return NoteLetter(new_value)

    def __sub__(self, other: int) -> "NoteLetter":
        """
        When subtracting letters, treat them as integers and wrap around if necessary.
        """
        new_value = (self.value - other) % len(NoteLetter)
        return NoteLetter(new_value)

    # @property
    # def distances_to_c(self) -> tuple[int,int]:
    #     """
    #     Returns how many semitones this note is away from C in both directions.
    #     """
    #     match self:
    #         case NoteLetter.C:
    #             return (0,12)
    #         case NoteLetter.D:
    #             return (2,10)
    #         case NoteLetter.E:
    #             return (4,8)
    #         case NoteLetter.F:
    #             return (5,7)
    #         case NoteLetter.G:
    #             return (7,5)
    #         case NoteLetter.A:
    #             return (9,3)
    #         case NoteLetter.B:
    #             return (11,1)

    @property
    def __int__(self) -> int:
        return self.value

    @classmethod
    def from_str(cls, s: str) -> "NoteLetter":
        """
        Converts a string to a NoteLetter by matching the string with the name of each enum variant.
        """
        for note in cls:
            if note.name == s:
                return note
        raise ValueError(f"Invalid note letter string: {s}")


class NoteAlteration(Enum):
    """
    Enum representing musical note alterations.
    """

    SHARP = 1
    FLAT = -1
    NATURAL = 0

    @property
    def semitone_difference(self) -> int:
        """
        Returns how many semitones this alteration modifies the note by.
        """
        return self.value

    def __int__(self) -> int:
        return self.semitone_difference

    def __str__(self):
        match self:
            case NoteAlteration.SHARP:
                return "♯"
            case NoteAlteration.FLAT:
                return "♭"
            case NoteAlteration.NATURAL:
                return "♮"

    @classmethod
    def from_str(cls, s: str) -> "NoteAlteration":
        match s:
            case "♯":
                return cls.SHARP
            case "#":
                return cls.SHARP
            case "♭":
                return cls.FLAT
            case "b":
                return cls.FLAT
            case "♮":
                return cls.NATURAL
            case "n":
                return cls.NATURAL
            case _:
                raise ValueError(f"Invalid alteration string: {s}")



class Note:
    """
    An abstract musical note, without a specific octave.
    """

    def __init__(self, letter: NoteLetter, alteration: NoteAlteration):
        self.letter = letter
        self.alteration = alteration

    @classmethod
    def from_str(cls, s: str) -> Self:
        """
        Allows creating a Note from a string representation like "C♯" or "D♭".
        """
        if len(s) == 1:
            return cls(NoteLetter.from_str(s), NoteAlteration.NATURAL)
        elif len(s) == 2:
            letter = NoteLetter.from_str(s[0])
            alteration = NoteAlteration.from_str(s[1])
            return cls(letter, alteration)
        else:
            raise ValueError(f"Invalid note string: {s}")

    @property
    def distances_to_c(self) -> tuple[int,int]:
        """
        Returns how many semitones away from C this note is in both directions.
        """
        note_letter_c_distances = self.letter.distances_to_c
        match self.alteration:
            case NoteAlteration.SHARP:
                return (
                    note_letter_c_distances[0] + 1,
                    note_letter_c_distances[1] - 1,
                )
            case NoteAlteration.FLAT:
                return (
                    note_letter_c_distances[0] - 1,
                    note_letter_c_distances[1] + 1,
                )

    @classmethod
    def from_semitone_offset(cls, semitone_offset: int) -> set[Self]:
        """
        Returns all possible notes that are a specific number of semitones away from C

        Edge cases:
        - from_semitone_offset(0) == {C, B♯}
        - from_semitone_offset(11) == {B, C♭}
        """
        if semitone_offset < 0 or semitone_offset > 11:
            raise ValueError("Semitone offset must be between 0 and 11")

        # Loop through all possible letters and alterations
        notes = set(
            cls(letter, alteration)
            for letter in NoteLetter
            for alteration in NoteAlteration
            if (letter.semitone_offset + alteration.semitone_difference) % 12
            == semitone_offset
        )

        return notes

    def __eq__(self, other: object) -> bool:
        """
        Two non-octaved notes are equal if they have the same semitone offset.
        """
        if not isinstance(other, Note):
            return NotImplemented
        return self.semitone_offset == other.semitone_offset

    # lt is not implemented because it doesn't make sense to compare notes without an octave

    def __str__(self):
        return (
            f"{self.letter}{self.alteration}"
            if self.alteration != NoteAlteration.NATURAL
            else str(self.letter)
        )

    def __repr__(self):
        return f"Note({self.letter!r}, {self.alteration!r})"

    def __hash__(self) -> int:
        return hash((self.letter, self.alteration))

class Interval(Enum):
    """
    Enum representing musical intervals with their semitone and letter distances.
    """

    MAJOR_THIRD = (4, 2)  # 4 semitones, 2 letter steps
    MINOR_THIRD = (3, 2)  # 3 semitones, 2 letter steps
    PERFECT_FIFTH = (7, 4)  # 7 semitones, 4 letter steps

    @property
    def semitone_distance(self) -> int:
        """
        Get the semitone distance of the interval.
        """
        return self.value[0]

    @property
    def letter_distance(self) -> int:
        """
        Get the letter distance of the interval.
        """
        return self.value[1]



@total_ordering
class NoteInOctave:
    """
    A concrete musical note in a specific octave
    """

    def __init__(self, note: Note, octave: int):
        self.note = note
        self.octave = octave

    # def from_semitone_distance(self, semitone_distance: int) -> set["NoteInOctave"]:
    #     """
    #     Returns all possible notes that are a specific number of semitones away from this note
    #     """
    #     # Add semitones representing interval
    #     new_semitone_offset = self.semitone_offset + semitone_distance

    #     # Possibly wrap around semitones and modify octave
    #     new_octave = self.octave
    #     if new_semitone_offset > 11:
    #         new_octave += new_semitone_offset // 12
    #         new_semitone_offset = new_semitone_offset % 12
    #     elif new_semitone_offset < 0:
    #         new_octave -= new_semitone_offset // 12
    #         new_semitone_offset = 12 - abs(new_semitone_offset) % 12

    #     # There are multiple possible notes that can be represented by a specific semitone offset
    #     new_notes = Note.from_semitone_offset(new_semitone_offset)

        # There are two edge cases where we need to adjust the octave:
        # octave_offsets = [
        #     -1
        #     if note == Note(NoteLetter.B, NoteAlteration.SHARP)
        #     else 1
        #     if note == Note(NoteLetter.C, NoteAlteration.FLAT)
        #     else 0
        #     for note in new_notes
        # ]

        # return set(
        #     NoteInOctave(new_note, new_octave + octave_offset)
        #     for new_note, octave_offset in zip(new_notes, octave_offsets)
        # )

        # return set(NoteInOctave(new_note, new_octave) for new_note in new_notes)

    def from_semitone_distance(self, semitone_offset: int) -> set[Self]:
        """
        Returns all possible notes that are a specific number of semitones away from this note
        """

        new_absolute_semitone_offset = self.absolute_semitone_offset + semitone_offset

        # Canditate new octave, may have to be adjusted in two edge cases
        new_octave = new_absolute_semitone_offset // 12

    def __add__(self, interval: Interval) -> "NoteInOctave":
        """
        Adds an interval to the note, potentially changing its octave.
        """

        # Find all possible notes that are a specific number of semitones away from this note
        feasible_notes = self.from_semitone_distance(interval.semitone_distance)

        # Only one of these notes will have the correct letter
        new_notes = [
            note
            for note in feasible_notes
            if note.letter - interval.letter_distance == self.letter
        ]
        assert len(new_notes) == 1, (
            "There should only be one correct note after adding an interval"
        )
        new_note = new_notes[0]

        return new_note

    def __str__(self):
        return f"{self.note}{self.octave}"

    @property
    def absolute_semitone_offset(self) -> int:
        """
        The absolute semitone offset of the note is the semitone offset from C0.
        """
        # Note that we cannot use note.semitone_offset directly here because it wraps around
        absolute_semitone_offset = 12*self.octave + self.note.letter.semitone_offset + self.note.alteration.semitone_difference

        return absolute_semitone_offset


    def __int__(self):
        """
        The integer representation of the note is absolute semitone offset.
        """
        return self.absolute_semitone_offset

    def __repr__(self):
        return f"NoteInOctave({self.note!r}, {self.octave!r})"

    def __eq__(self, other: object) -> bool:
        """
        Comparison is forwarded to the absolute semitone offset.
        """
        assert isinstance(other, NoteInOctave), (
            "Cannot compare NoteInOctave with non-NoteInOctave object"
        )
        return self.absolute_semitone_offset == other.absolute_semitone_offset

    def __lt__(self, other: object) -> bool:
        """
        Comparison is forwarded to the absolute semitone offset.
        """
        assert isinstance(other, NoteInOctave), (
            "Cannot compare NoteInOctave with non-NoteInOctave object"
        )
        return self.absolute_semitone_offset < other.absolute_semitone_offset

    def __hash__(self) -> int:
        return hash((self.note, self.octave))

    @classmethod
    def from_str(cls, s: str) -> Self:
        """
        Converts a string to an octaved note by splitting the string into note and octave parts.

        Examples: NoteInOctave.from_str("C4"), NoteInOctave.from_str("D♯5"), NoteInOctave.from_str("B♭3")
        """
        note_str = s[:-1]
        octave_str = s[-1]
        note = Note.from_str(note_str)
        octave = int(octave_str)
        return cls(note, octave)

    # Forward some properties to the underlying note to avoid breaking law of demeter
    @property
    def letter(self) -> NoteLetter:
        return self.note.letter

    @property
    def alteration(self) -> NoteAlteration:
        return self.note.alteration

    # @property
    # def semitone_offset(self) -> int:
    #     return self.note.semitone_offset



class Chord:
    """
    A Chord is a set of octaved notes.
    """

    def __init__(self, notes: set[NoteInOctave]):
        self.notes = notes

    def __iter__(self):
        return iter(self.notes)
