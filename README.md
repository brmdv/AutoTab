# AutoTab
Convert ASCII lyrics with guitar chords to LaTeX compatible [leadsheets](https://github.com/cgnieder/leadsheets). 

The LaTeX package *leadsheets* uses a specific syntax to write chords on lyrics:

```latex
This ^{Am}is a sen^*{F}ten ce in ^-{Gm}a song \\
```

 However, on the internet, the common way to represent guitar tabs is like this:

```
     Am      F        Gm
This is a sentence in a  song
```

This script converts the latter style to the former. It uses [PyHyphen](https://pypi.org/project/PyHyphen/) to automatically split long words into syllables, so that chords are better aligned.


## Dependancies 

You need *pyhyphen* and *argparse*. Install with

```bash
$ pip install pyhyphen argparse
```

## Usage

```bash
$ python autotab.py [-h] [-o OUTPUT] [-l LANG] [--full_words] [--punct]
               [--overlap {always,never,auto}] [--version] [--verbose]
               input file
```

###  Arguments

* `-h`: show help
* `-o OUTPUT`: enter file name `OUTPUT` where output will be saved. If not specified, output is printed in terminal.
* `-l` or `--lang`: Language of the lyrics. Is important for splitting long words in syllables. Language is written as `en_US`, i.e. two character language code, followed by two character country code. 
* `--full_words`: Don't split words in syllables. So no automatic `^*{}` functionality.
* `--punct`: Punctuation marks are also split, e.g. instead of `^{}test,` you'll get `^*{}test ,`.
* `--overlap {always,never,auto}`: changes usage of `-` in the chords.
  * `always` en `never`: speaks for itself
  * `auto`: (default) Adds `-` to chord when number of characters in chords is equal to or greater than characters in accompanying syllable
* `--version`: version number
* `--verbose`: more information during runtime.

### Example

1. Simple conversion of an English  song.

   ```bash
   $ python autotab.py hotelcalifornia.txt
   ```

2. Write to file, specify language and center chords above words without punctuation.

```bash
$ python autotab.py --lang en_US --punct --verbose -o hotelcali_out.tex hotelcalifornia.txt
```
