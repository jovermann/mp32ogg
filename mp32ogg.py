#!/usr/bin/env python
#
# mp32ogg.py - Convert a directory tree full of mp3s to a directory tree full of *.oggs with 22050 Hz and mono.
#
# Copyright (C) 2015 by Johannes Overmann <Johannes.Overmann@joov.de>

# v0.0.1 works
# v0.0.2 ignore files which are already processed

import optparse
import sys
import glob
import os
import re


def isWindows():
    """Return true iff the hist operating system is Windows.
    """
    return os.name == "nt"


def isdigit(char):
    """Return True iff char is a digit.
    """
    return char.isdigit()
    

def isalpha(char):
    """Return True iff char is a letter.
    """
    return char.isalpha()
    

class Error:
    """
    """
    def __init__(self, message):
        self.message = message
        
        
def writeStringToFile(fileName, s):
    """Write string to file.
    """
    f = open(fileName, "wb")
    f.write(s)
    f.close()
    
    
def readStringFromFile(fileName):
    """Read string from file and return it.
    """
    f = open(fileName, "rb")
    r = f.read()
    f.close()
    return r


def run(cmd):
    """Run command.
    """
    if options.verbose:
        print "Running " + cmd
    if isWindows():
        cmd = cmd.replace("/", "\\")
        cmd = cmd.replace("'", '"')
    if os.system(cmd):
        raise Error("Command failed: " + cmd)

        
def removeFiles(pattern):
    """Remove files matching glob pattern.
    """
    for f in glob.glob(pattern):
        os.remove(f)
    
        
def mkdir(path):
    """Make directory if it does not yet exist. Recursively.
    """
    if not path:
        return
    if os.path.isdir(path):
        return
    mkdir(os.path.dirname(path))
    os.mkdir(path)

    
def sanitizeFilename(path):
    """Replace all non-printable and space chars with underscores.
    """
    r = path.replace("a\xcc\x88", "ae")
    r = path.replace("o\xcc\x88", "oe")
    r = path.replace("u\xcc\x88", "ue")
    r = path.replace("A\xcc\x88", "Ae")
    r = path.replace("O\xcc\x88", "Oe")
    r = path.replace("U\xcc\x88", "Ue")
    r = path.replace("\xc3\x9f", "ss")
    r = r.replace(" - ", "_")
    r = r.replace(" ", "_")
    r = r.replace("-", "_")
    r = re.sub("[^0-9a-zA-Z._/]", "", r)
    return r


def processFile(inpath, outpath):
    """Convert file to ogg.
    """
    # Ignore if outpath already exists.
    if os.path.exists(outpath):
        return

    print inpath, "->", outpath
    if options.dummy:
        return

    # Copy mp3 to filename without spaces.
    f = open(inpath, "rb")
    mp3data = f.read()
    f.close()
    f = open("tmp.mp3", "wb")
    f.write(mp3data)
    f.close()
    
    # Make outdir
    mkdir(os.path.dirname(outpath))
    
    # Convert mp3 to wav.
    run("mpg123 -w tmp.wav tmp.mp3")
    
    # Convert wav to ogg.
    run("oggenc tmp.wav --downmix --resample 22050 -o " + outpath)
    

def main():
    global options
    usage = """Usage: %prog INDIR [OUTDIR]

Convert all *.mp3 files found in INDIR to *.ogg files in OUTDIR with 22050 Hz and in mono.
This tool needs mpg123 and oggenc on the path.
"""
    version = "0.0.1"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-d", "--dummy",  default=False, action="store_true", help="Dummy mode. Nothing changes on disk.")
    parser.add_option("-v", "--verbose",  default=0, action="count", help="Be more verbose.")
    (options, args) = parser.parse_args()

    if len(args) not in (1, 2):
	parser.error("Please specify INDIR [OUTDIR].")
    if len(args) < 2:
        args.append("ogg")
    indir = args[0]
    outdir = args[1]
        

    try:
        if os.path.isdir(indir):
            for root, dirs, files in os.walk(indir):
                subdir = root[len(indir) + 1:]
                for localfile in files:
                    if not localfile.lower().endswith(".mp3"):
                        continue
                    if localfile.startswith("._"):
                        continue
                    path = subdir + "/" + localfile
                    inpath = indir + "/" + path
                    outpath = outdir + "/" + path
                    outpath = sanitizeFilename(outpath)
                    outpath = re.sub("[.]mp3$", ".ogg", outpath)
                    processFile(inpath, outpath)
        elif os.path.isfile(indir):
            inpath = indir
            path = os.path.basename(inpath)
            outpath = outdir + "/" + path
            outpath = sanitizeFilename(outpath)
            outpath = re.sub("[.]mp3$", ".ogg", outpath)
            processFile(inpath, outpath)
        else:
            print "%s not found" % indir
            

        removeFiles("tmp.mp3")
        removeFiles("tmp.wav")


    except Error as e:
        print "Error:", e.message
        sys.exit(1)
    
    

# call main()
if __name__ == "__main__":
    main()

