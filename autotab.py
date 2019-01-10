import re
import argparse
from hyphen import Hyphenator

version=0
subversion=1


# parser definition + arguments
parser = argparse.ArgumentParser(description='Convert ASCII guitar tabs to LaTeX compatible leadsheets.', prog='AutoTab')


parser.add_argument('-o','--output', help='write output to file', type=argparse.FileType('w'))

parser.add_argument('-l', '--lang', help='source language, usefull for correct syllables (default: \'en_US\')', default='en_US')
parser.add_argument('--full_words', help='don\'t split words in syllables', action='store_true')
parser.add_argument('--punct', help='split adjacent punctuation, e.g. \'^*{A}example ,\'', action='store_true')
parser.add_argument('--overlap', help='set length for using ^-{} in stead of ^{} (default: auto)', choices=['always', 'never', 'auto'], default='auto')

parser.add_argument('--version', action='version', version='%s %d.%d'%(parser.prog, version,subversion))
parser.add_argument('--verbose', '-v', action='store_true', help='show more (debug) information')

parser.add_argument('input', metavar='input file', type=argparse.FileType('r'))

args=parser.parse_args()

verbose=args.verbose

#################### HELPER FUNCTIONS

def isChordLn(line):
    return bool(re.match(r'^\s*([A-G]\S*\s*)+$', line))

def prnLine(num, lines):
    print(lines[num]['chords'])
    print(lines[num]['text'])

def interval(value, ls):
    ls=sorted(list(set(ls)))
    if value<ls[0]:
        return (None,ls[0])
    for i, val  in enumerate(ls[1:]):
        if value<val:
            return (ls[i], val)
    if value>= ls[-1]:
        return (ls[-1],None)

####################

   
if not args.full_words:
    try:
        hyph = Hyphenator(args.lang)
    except:
        if verbose:
            print('WARNING: could not fetch dictionary for %s, using --full_words.'%(args.lang))
            args.full_words=True

data=args.input.read().split('\n')
args.input.close()

if verbose:
    print('Running AutoTab %d.%d...'%(version, subversion))
    print('input:  '+args.input.name)
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
        splitted_lines.append([{'text': line['text'], 'chord': None, 'loose': True }])
    else:
        # make same length
        chordline=line['chords']+' '
        textline=line['text']+' '
        length=max(len(chordline), len(textline))
        chordline=chordline.ljust(length, ' ')
        textline=textline.ljust(length, ' ')

        # split text into words and, if necessary, syllables
        wordstarts=[]
        syllstarts=[]

        ## find word positions
        prevchar=''
        splitchars=' \t.,;:\'"-()[]{}'
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
        if position>=0: 
            chorded_parts.append((interval(position,break_positions),current_chord))
        ## add to list
        current=[]
        ### add everything before first chord
        if chorded_parts[0][0][0]:
            current.append({'text': textline[0:chorded_parts[0][0][0]], 'chord': None, 'loose':True})
        ### add middle
        for i,part in enumerate(chorded_parts):
            current.append({
                'text': textline[part[0][0]:part[0][1]],
                'chord': part[1],
            })

            if not part[0][1] or i==len(chorded_parts)-1:
                current[-1]['loose']=True
            elif args.punct:
                current[-1]['loose']=textline[part[0][1]]==' ' 
            else:
                current[-1]['loose']=textline[part[0][1]] in splitchars

            #### add normal text inbetween
            if part[0][1] and i<len(chorded_parts)-1:
                current.append({
                    'text': textline[part[0][1]:chorded_parts[i+1][0][0]],
                    'chord': None,
                    'loose': True
                })
        ### add everything behind last chord
        if chorded_parts[-1][0][1]:
            current.append({'text': textline[chorded_parts[-1][0][1]:], 'chord': None, 'loose':True})

        ### add to all
        splitted_lines.append(current)

# output

if verbose:
    print('* Creating output LaTeX.')

output_text = ''

for line in splitted_lines: 
    for piece in line:
        if len(piece['text'].strip())==0:
            output_text+=' '
        if piece['chord']: 
            #overlap
            if args.overlap=='always':
                overlap='-'
            elif args.overlap=='auto':
                if len(piece['chord'])>=len(piece['text']):
                    overlap='-'
                else:
                    overlap=''
            else:
                overlap=''
            output_text+='^%s%s{%s}'%('*' if not piece['loose'] else '', overlap, piece['chord'])
        if len(piece['text'].strip())==0:
            output_text+=''
        else:
            output_text+=piece['text'].replace('[', '$[$').replace(']', '$]$')
        if not piece['loose']:
            output_text+=' '
    output_text+=' \\\\\n' 

if args.output:
    if verbose:
        print('* Writing to ' + args.output.name)
    args.output.write(output_text)
    args.output.close()
else:
    if verbose:
        print('* Output:\n[[')
    print(output_text)
    if verbose:
        print(']]')

if verbose:
    print('* Done.')