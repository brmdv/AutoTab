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

#################### HELPER FUNCTIONS

def isChordLn(line):
    return bool(re.match(r'^\s*([A-G]\S*\s*)+$', line))

def prnLine(num, lines):
    print(lines[num]['chords'])
    print(lines[num]['text'])

def interval(value, ls):
    ls=list(set(ls))
    if value<ls[0]:
        return (None,ls[0])
    for i, val  in enumerate(ls[1:]):
        if value<val:
            return (ls[i], val)
    if value>= ls[-1]:
        return (ls[-1],None)

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

        # split text into words and, if necessary, syllables
        wordstarts=[]
        syllstarts=[]

        ## find word positions
        prevchar=''
        splitchars=' \t.,;:\'"-'
        for i, char in enumerate(textline):
            if char not in splitchars and prevchar in splitchars:
                wordstarts.append(i)
            elif char in splitchars and prevchar not in splitchars:
                wordstarts.append(i)
            prevchar=char

        ## find syllable positions
        if not args.full_words:
            for idx in range(len(wordstarts)-1):
                sylls=hyph.syllables(textline[wordstarts[idx]:wordstarts[idx+1]])
                if len(sylls)>1:
                    for s in sylls[:-1]:
                        syllstarts.append(wordstarts[idx]+len(s))

        # join text into parts that are separated by chords
        ## find chord positions
        prevchar=''
        current_chord=''
        position=-1
        break_positions=list(set(syllstarts+wordstarts))
        chorded_parts=[]
        for i, char in enumerate(chordline):
            # start of chord
            if char!=' ' and (prevchar=='' or prevchar==' '):
                position=i
                current_chord+=char
            elif (char==' ' or i==len(chordline)-1) and position>=0:
                # end of chord
                chorded_parts.append((interval(position,break_positions),current_chord))

                current_chord=''
                position=-1
            elif position>=0:
                current_chord+=char

            prevchar=char
        if position>=0: chorded_parts.append((interval(position,break_positions),current_chord))
    pass
        
