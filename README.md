
# SUBSUB Segmenter

This repository contains Python 3.6+ text segmentation scripts for machine translation.

## The main principles

  - Performs word segmentation for machine translation.
  - Segmentation is potentially done into two parts -- main part and endin part.

## Usage instructions

SUBSUB is used in the following way:
  - Learning phase (segmentation model produced): [learn_subsub.py]
  - Segmentation phase (using segmentation model obtained in the previous phase): [apply_subsub.py]
  - Removing segmentation: [unprocess_subsub.py]

### Phase #1. Learning ([learn_subsub.py])

During this phase, segmentation {model} is produced from the {corpus}. Segmentation model contains information about potential stems (roots) and endings (suffixes).

**Running the learning script**:

```sh
learn_subsub.py -i {corpus} -o {model}
```

**Additional optional parameters for the learning script**:
  - initial global potential endings rate (e, default: 300): Rate of right substrings to become potential endings. For less inflected languages should be less (e.g., 100 for English).
  - initial local potential endings rate (f, default: 10): Maximum amount of right substrings for a stem to collect initial set of potential endings.


### 2. Segmentation ([apply_subsub.py])

During this phase, {input text} is segmented using segmentation {model} obtained in the learning phase.

**Running the segmentation script**:

```sh
apply_subsub.py -i {input text} -s {model} -o {output text}
```

**Additional optional parameters for the segmentation script**:

  - segmentation suppress rate (w, default: 1.0) - Word occurrence rate to suppress segmentation (if occurrence of the word in the learning corpus was big enough, word is not segmented at all; if parameter set to 0.0, word occurrence doesn't affect segmentation).
  - segmentation marker (m, default: '9474') -- a character or sequence of character to mark segments to constitute words (if sequence of digits, then is converted to the character represented by that number).
  - uppercase marker (n, default: '9553') -- a character or sequence of character to mark next word as starting with uppercase (if sequence of digits, then is converted to the character represented by that number).

#### Segmentation examples (segmentation mark is '@', uppercase mark is '$')

##### Example of segmentation #1: Latvian

septiņ @os vēl @ēšanu apgabal @os viens ar otr @u savstarpēj @i sacenš @as vald @ošās koalīcij @as part @iju kandidāt @i .

##### Example of segmentation #2: English

I apologis @e for appear @ing positive every now and then .

##### Example of segmentation #3: English without suppressing segmentation due to word frequencies

I apologis @e fo @r appear @ing positiv @e ever @y no @w an @d th @en .

##### Example of segmentation #4: Russian

$ значительн @ая част @ь мир @а управля @ется таким образом. $ но на этом общем фон @е $ франция имеет несколько важн @ых отличительн @ых черт.


### 3. Removing segmentation ([unprocess_subsub.py])

During this operation, a segmented text is converted back to a normal text:

```sh
unprocess_subsub.py -i {input text} -o {output text}
```

**Additional optional parameters for the desegmentation script**:

  - segmentation marker (m, default: '9474') -- a character or sequence of character to mark segments to constitute words (if sequence of digits, then is converted to the character represented by that number).
  - uppercase marker (n, default: '9553') -- a character or sequence of character to mark next word as starting with uppercase (if sequence of digits, then is converted to the character represented by that number).


   [learn_subsub.py]: <https://github.com/zuters/subsub/learn_subsub.py>
   [apply_subsub.py]: <https://github.com/zuters/subsub/apply_subsub.py>
   [unprocess_subsub.py]: <https://github.com/zuters/subsub/unprocess_subsub.py>
