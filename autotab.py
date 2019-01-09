import re
import argparse
from hyphen import Hyphenator

version=0
subversion=0


# parser definition + arguments
parser = argparse.ArgumentParser(description='Convert ASCII guitar tabs to LaTeX compatible leadsheets.')

parser.add_argument('--version',  action='store_true', help='show version number')
parser.add_argument('--verbose', '-v', action='store_true', help='show more (debug) information')
parser.add_argument('-o', '--output', help='write output to file', type=argparse.FileType('w'))
parser.add_argument('-l', '--lang', help='source language', default='en_US')
parser.add_argument('--full_words', help='don\'t split syllables', action='store_true')
parser.add_argument('--split_punct', help='split adjacent punctuation', action='store_true')
parser.add_argument('--overlap_thr', help='set length for using ^-{} in stead of ^{}, default: 1', type=int, default=1)

parser.add_argument('input', type=argparse.FileType('r'))

args=parser.parse_args()

verbose=args.verbose

####################

def isChordLn(line):
    return bool(re.match(r'^\s*([A-G]\S*\s*)+$', line))

def prnLine(num, lines):
    print(lines[num]['chords'])
    print(lines[num]['text'])

####################

if args.version and not verbose:
    print ("AutoTab %d.%d"%(version, subversion))
    
if not args.full_words:
    hyph = Hyphenator(args.lang)

data=args.input.read().split('\n')
args.input.close()

if verbose:
    print('Running AutoTab %d.%d...'%(version, subversion))
    print('inputfile: '+args.input.name)
    if args.output: print('output: '+ args.output.name)


# loop through lines and combine with chords

lastchordline=''
lines=[]

for line in data:
    if isChordLn(line): 
        lastchordline=line

    else:
        if len(line.strip())==0:
            continue

        newline={'text': line}
        if len(lastchordline)>0:
            newline['chords']= lastchordline
            lastchordline=''

        lines.append(newline)

if verbose:
    count_chords=0
    for line in lines:
        if 'chords' in line: count_chords+=1
    print('* file successfully imported. %d textlines, whereof %d with chords'%(len(lines), count_chords))

# create split measures
splitted_lines=[]
if not args.full_words:
    if verbose:
        print('* splitting words in syllables')
for line in lines:
    if not 'chords' in line.keys():
        splitted_lines.append([[line['text'], '']])
    else:
        # make same length
        chordline=line['chords']
        textline=line['text']
        length=max(len(chordline), len(textline))
        chordline=chordline.ljust(length, ' ')
        textline=textline.ljust(length, ' ')

        # split text into syllables
        wordstarts=[]
        syllstarts=[]

        prevchar=''
        splitchars=' \t.,;:\'"-'
        for i, char in enumerate(textline):
            if char not in splitchars and prevchar in splitchars:
                wordstarts.append(i)
            prevchar=char

        wordstarts.append(length)
        if not args.full_words:
            if verbose:
                print('* splitting words in syllables')
            syllables=hyph.syllables(textline)
            for s in syllables:
                syllstarts.append(len(s)+sum(syllstarts))
            print(syllstarts)