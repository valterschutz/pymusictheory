from pymusictheory import Interval, Note, NoteAlteration, NoteInOctave, NoteLetter


class TestNoteLetter:
    def test_addition(self):
        actual = [
            NoteLetter.C + 4,
            NoteLetter.E + 7,
            NoteLetter.A + 2,
        ]

        expected = [
            NoteLetter.G,
            NoteLetter.E,
            NoteLetter.C,
        ]

        assert actual == expected, f"Expected {expected}, but got {actual}"

    def test_subtraction(self):
        actual = [
            NoteLetter.C - 4,
            NoteLetter.E - 7,
            NoteLetter.A - 2,
        ]

        expected = [
            NoteLetter.F,
            NoteLetter.E,
            NoteLetter.F,
        ]

        assert actual == expected, f"Expected {expected}, but got {actual}"


class TestNote:
    def test_semitone_offset(self):
        actual = [
            Note.from_str("C").semitone_offset,
            Note.from_str("E♭").semitone_offset,
            Note.from_str("F♯").semitone_offset,
        ]

        expected = [
            0,
            3,
            6,
        ]

        assert actual == expected, f"Expected {expected}, but got {actual}"

    def test_from_semitone_offset(self):
        actual = [
            Note.from_semitone_offset(0),
            Note.from_semitone_offset(3),
            Note.from_semitone_offset(5),
            Note.from_semitone_offset(11),
        ]

        expected = [
            {
            Note.from_str("B♯"),
            Note.from_str("C"),
            },
            {
            Note.from_str("D♯"),
            Note.from_str("E♭"),
            },
            {
            Note.from_str("E♯"),
            Note.from_str("F"),
            },
            {
            Note.from_str("B"),
            Note.from_str("Cb"),
            },
        ]

        assert actual == expected, f"Expected {expected}, but got {actual}"

    def test_eq(self):
        # Should be equal
        assert Note.from_str("C") == Note.from_str("C")
        assert Note.from_str("C♭") == Note.from_str("B")
        assert Note.from_str("C") == Note.from_str("B♯")
        assert Note.from_str("E♯") == Note.from_str("F")
        assert Note.from_str("G♯") == Note.from_str("Ab")
        # Should not be equal
        assert Note.from_str("C") != Note.from_str("D")
        assert Note.from_str("C") != Note.from_str("C♭")


class TestNoteInOctave:
    def test_eq(self):
        # Should be equal
        assert NoteInOctave.from_str("C4") == NoteInOctave.from_str("C4")
        assert NoteInOctave.from_str("C♭4") == NoteInOctave.from_str("B3")
        assert NoteInOctave.from_str("C4") == NoteInOctave.from_str("B♯3")
        assert NoteInOctave.from_str("E♯4") == NoteInOctave.from_str("F4")
        assert NoteInOctave.from_str("G♯4") == NoteInOctave.from_str("Ab4")
        # Should not be equal
        assert NoteInOctave.from_str("C4") != NoteInOctave.from_str("D4")
        assert NoteInOctave.from_str("C4") != NoteInOctave.from_str("C♭5")



    def test_from_semitone_distance(self):
        actual = [
            NoteInOctave.from_str("C4").from_semitone_distance(0),
            NoteInOctave.from_str("Cb4").from_semitone_distance(0),
            NoteInOctave.from_str("B#4").from_semitone_distance(0),
            NoteInOctave.from_str("G4").from_semitone_distance(5),
            NoteInOctave.from_str("A3").from_semitone_distance(5),
            NoteInOctave.from_str("A3").from_semitone_distance(6),
        ]

        expected = [
            {
                NoteInOctave.from_str("C4"),
                NoteInOctave.from_str("B♯3"),
            },
            {
                NoteInOctave.from_str("Cb4"),
                NoteInOctave.from_str("B3"),
            },
            {
                NoteInOctave.from_str("B#4"),
                NoteInOctave.from_str("C5"),
            },
            {
                NoteInOctave.from_str("C5"),
                NoteInOctave.from_str("B♯4"),
            },
            {
                NoteInOctave.from_str("D4"),
            },
            {
                NoteInOctave.from_str("D♯4"),
                NoteInOctave.from_str("E♭4"),
            },
        ]

        assert actual == expected, f"Expected {expected}, but got {actual}"

    def test_add_interval(self):
        """
        Test that adding intervals works as expected.

        Tested so far (in octave 4):
        - MINOR_THIRD
        - MAJOR_THIRD
        - PERFECT_FIFTH

        Also tested a perfect fifth with a different octave.
        """

        # Minor thirds
        roots = [
            NoteInOctave.from_str("C4"),
            NoteInOctave.from_str("C♯4"),
            NoteInOctave.from_str("D4"),
        ]

        minor_thirds = [root + Interval.MINOR_THIRD for root in roots]

        expected = [
            NoteInOctave.from_str("E♭4"),
            NoteInOctave.from_str("E4"),
            NoteInOctave.from_str("F4"),
        ]

        assert minor_thirds == expected, f"Expected {expected}, but got {minor_thirds}"

        # Major thirds
        roots = [
            NoteInOctave.from_str("C4"),
            NoteInOctave.from_str("C♯4"),
            NoteInOctave.from_str("D4"),
        ]

        major_thirds = [root + Interval.MAJOR_THIRD for root in roots]

        expected = [
            NoteInOctave.from_str("E4"),
            NoteInOctave.from_str("E♯4"),
            NoteInOctave.from_str("F♯4"),
        ]

        assert major_thirds == expected, f"Expected {expected}, but got {major_thirds}"

        # Perfect fifths
        roots = [
            NoteInOctave.from_str("C4"),
            NoteInOctave.from_str("C♯4"),
            NoteInOctave.from_str("D4"),
        ]

        perfect_fifths = [root + Interval.PERFECT_FIFTH for root in roots]

        expected = [
            NoteInOctave.from_str("G4"),
            NoteInOctave.from_str("G♯4"),
            NoteInOctave.from_str("A4"),
        ]

        assert perfect_fifths == expected, (
            f"Expected {expected}, but got {perfect_fifths}"
        )

        # Perfect fifths in different octaves
        roots = [
            NoteInOctave.from_str("G4"),
            NoteInOctave.from_str("G♯4"),
            NoteInOctave.from_str("A♭4"),
        ]

        perfect_fifths = [root + Interval.PERFECT_FIFTH for root in roots]

        expected = [
            NoteInOctave.from_str("D5"),
            NoteInOctave.from_str("D♯5"),
            NoteInOctave.from_str("E♭5"),
        ]

        assert perfect_fifths == expected, (
            f"Expected {expected}, but got {perfect_fifths}"
        )
