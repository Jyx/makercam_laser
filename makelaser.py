#!/usr/bin/python
import re
import sys
import getopt

# Default feedrate
FEED_RATE = 200
SETUP = 0
LASER_ON = 1
LASER_OFF = 2

def read_file(filename):
    gcode = []
    f = open(filename, 'r')
    gcode = f.readlines()
    f.close()
    return gcode
        
def convert_to_laser(gcode, filename):
    mode = SETUP
    last_mode = SETUP
    setup_done = False
    laser_file = open(filename, 'w')
    laser_file.write("; Converted from Makercam gcode to a more\n" +
            "; laser friendly code using:\n" + 
            ";   https://github.com/Jyx/makercam_laser\n" +
            "; by Joakim Bech\n")

    laser_file.write("F" + str(FEED_RATE) + "\n")

    setup = True
    for g in gcode:
        if re.search(r'^G0{2}[^1234]', g):
            mode = LASER_OFF
            setup_done = True
        elif re.search(r'^G0?[1234][^0-9]', g):
            mode = LASER_ON
            setup_done = True
        else:
            mode = SETUP


        if mode == SETUP and not setup_done:
            # Remove all laser on before first movement, this should only be
            # reached once!
            g = re.sub(r'M3', '', g)
        elif mode == LASER_OFF:
            if last_mode == LASER_ON:
                laser_file.write("M5 (laser off)\n")
            last_mode = mode
        elif mode == LASER_ON:
            if last_mode == LASER_OFF:
                laser_file.write("M3 (laser on)\n")
            ## change feed rate
            g = re.sub(r'F\d*', "F" + str(FEED_RATE), g)
            last_mode = mode

        if mode != SETUP:
            # Remove all Z variables
            g = re.sub(r'Z-?\d*\.\d* ?', '', g)

            # Remove empty G00 lines. After cleaning lines containing Z
            # variables, it might be that we end up with lines only saying
            # "G00".
            # Take note here that the line contains non-printable characters, so
            # even though it looks like it contains only "GOO ", i.e, 4
            # characters, it also contains "\r\n" and therefore we need to match
            # all non-word characters.
            s = re.search("^.*G00\W*$", g, re.I)
            if s:
                continue

        laser_file.write(g)

    laser_file.close()

def main(argv):
    print "Makercam to laser"
    infile = ""
    outfile = ""

    try:
        opts, args = getopt.getopt(argv, "hi:o:f:")
    except getopt.GetoptError:
        print "makerlaser.py -i <infile> -o <outfile> -f <feed rate>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print "makerlaser.py -i <infile> -o <outfile> -f <feed rate>"
        elif opt == '-i':
            infile = arg
        elif opt == '-o':
            outfile = arg
        elif opt == '-f':
            global FEED_RATE
            FEED_RATE = arg

    if outfile == "":
        outfile = infile + ".laser"

    gcode = read_file(infile)
    convert_to_laser(gcode, outfile)

if __name__ == "__main__":
    main(sys.argv[1:])
