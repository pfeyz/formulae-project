Setup:

  $ pip install -r requirements.txt

Usage:

see number of utterance per speaker:

  $ python main.py speakerstats 01a.xml 01b.xml
  INV 231
  CHI 846
  MOT 1224

output all bigrams in files:

  $ python main.py allgrams 01a.xml 01b.xml
  at Parent
  Parent Lastname
  Lastname 's
  's house
  house with
  with Child
  Child Lastname
  Lastname and
  ...

output all trigrams in files, limiting to specific speakers:

  $ python main.py allgrams -n 3 -s CHI,MOT 01a.xml 01b.xml
  that 's okay
  February first nineteen
  first nineteen eighty
  nineteen eighty four
  she just turned
  just turned two
  ...
