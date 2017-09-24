# Wikipedia-Search-Engine

Search Engine on Wikipedia dump with support for field queries

## Requirements
* Python 2.6 or above
* Python libraries:
  * Porter Stemmer
  * XML Parser
  * NLTK

Index can be generated using:
```sh
  ./index.sh  "path_to_wiki_dump"
```
For Searching:
```sh
  python search.py
```
>Sample Query<br />
* Plain query </br>
* Field query: "C:Plane B:Bus T:Air"

Term Field Abbreviations: b:Body, t:Title e:External Link, c:Category

You can download a small dump to test run from [here](https://drive.google.com/file/d/0B9o5ykSODCIlOEJsUFZPbVVLU3c/view?usp=sharing).
