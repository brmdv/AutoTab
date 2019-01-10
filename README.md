# AutoTab
Convert ASCII lyrics with guitar chords to LaTeX compatible leadsheets.


## Dependancies 

You need *pyhyphen* and *argparse*. Install with

```bash
pip install pyhyphen argparse
```

## Usage

```bash
python autotab.py [-h] [-o OUTPUT] [-l LANG] [--full_words] [--punct]
               [--overlap {always,never,auto}] [--version] [--verbose]
               input file
```

###  Arguments:

* `-h`: show help
* `-o OUTPUT`: enter file name `OUTPUT` where output will be saved. If not specified, output is printed in terminal.
* `-l` or `--lang`: Language of the lyrics. Is important for splitting long words in syllables. Language is written as `en_US`, i.e. two character language code, followed by two character country code. 
* `--full_words`: Don't split words in syllables. So no automatic `^*{}` functionality.
* `--punct`: Punctuation marks are also split, e.g. instead of `^{}test,` you'll get `^*{}test ,`.
* `--overlap {always,never,auto}`: changes usage of `-` in the chords.
  * `always` en `never`: speaks for itself
  * `auto`: (default) Adds `-` to chord when number of characters in chords is equal to or greater than characters in accompanying syllable
* `--version`: versionnumber
* `--verbose`: more information during runtime.

### Example:

```bash
python autotab.py --lang en_US --punct --verbose -o hotelcali_out.tex hotelcalifornia.txt
```
