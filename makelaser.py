#!/usr/bin/python
import re
import sys
import getopt

# Default feedrate
FEED_RATE = 200

def read_file(filename):
    gcode = []
    f = open(filename, 'r')
    gcode = f.readlines()
    f.close()
    return gcode
        
def convert_to_laser(gcode, filename):
    laser_file = open(filename, 'w')
    laser_file.write("; Converted from Makercam gcode to a more\n" +
            "; laser friendly code using:\n" + 
            ";   https://github.com/Jyx/makercam_laser\n" +
            "; by Joakim Bech\n")
    for g in gcode:
        # Start by changing feed rate
        g = re.sub(r'F\d*', "F" + str(FEED_RATE), g)

        # Then enable laser for all negative Z movements
        g = re.sub(r'.*Z-\d*.*', "M3 (laser on)", g)

        # and disable laser for all positive Z movements
        g = re.sub(r'.*Z\d*.*', "M5 (laser off)", g)
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
