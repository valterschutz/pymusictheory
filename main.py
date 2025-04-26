import os
import re
import subprocess

def generate_chord_xml(notes: list[str]) -> str:
    """
    Generate MusicXML for a chord based on the given notes.
    Each note is represented as a string on the form 'X[b/#]Y',
    where X is the note name (C, D, E, etc.), b or # is optional, and Y is the octave number.
    """

    template_xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
<part-list>
    <score-part id="P1">
    <part-name>Music</part-name>
    </score-part>
</part-list>
<part id="P1">
    <measure number="1">
    <attributes>
        <divisions>1</divisions>
        <key>
        <fifths>0</fifths>
        </key>
        <clef>
        <sign>G</sign>
        <line>2</line>
        </clef>
    </attributes>

    {}

    </measure>
</part>
</score-partwise>
    """

    chord_xml = ""
    note_pattern = re.compile(r"^([A-G])([b#]?)(\d)$")

    for note in notes:
        match = note_pattern.match(note)
        if not match:
            raise ValueError(f"Invalid note format: {note}")
        step, alter, octave = match.groups()

        if alter == 'b':
            alter = '-1'
        elif alter == '#':
            alter = '1'
        else:
            alter = '0'

        chord_xml += f"""<note>
        <chord/>
        <pitch>
        <step>{step}</step>
        <alter>{alter}</alter>
        <octave>{octave}</octave>
        </pitch>
        <duration>4</duration>
        <type>whole</type>
    </note>
    """

    # Insert chord xml into template
    complete_xml = template_xml.format(chord_xml)

    return complete_xml

# Function to generate MusicXML file and call MuseScore
def main():
    xml = generate_chord_xml(["C4", "Eb4", "G#4"])

    # Write xml to temporary file
    with open("chord.xml", "w") as file:
        file.write(xml)
    print("MusicXML file 'chord.xml' has been generated.")

    # Run `mscore` command to generate png image
    try:
        subprocess.run(["mscore", "chord.xml", "-o", "chord.png", "-T", "50"], check=True)
        print("MuseScore has generated 'chord.png'.")
    except subprocess.CalledProcessError as e:
        print(f"Error generating image: {e}")
    except FileNotFoundError:
        print("MuseScore is not installed or not found in PATH.")


if __name__ == "__main__":
    main()
