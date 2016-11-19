This project's main repo is available at [git.dragons.rocks](https://git.dragons.rocks/bookwyrm/).
Mirrors can be found on [GitHub](https://github.com/Tmplt/bookwyrm)
and [GitLab](https://gitlab.com/Tmplt/bookwyrm).

## What is this
Give `bookwyrm` some data which relates to a book, paper or similar.
With this data, it'll look trough all manners of sources (see [here](#planned-supported-sources)),
find some URIs, and then use an external downloader of your choice for processing.
By default, `bookwyrm` might use `aria2c`,
or perhaps something that all systems have at boot.
Not sure yet.

## Usage
```
usage: bookwyrm [-h] [-a AUTHOR] [-t TITLE] [-s SERIE] [-p PUBLISHER]
                [-y YEAR] [-l LANGUAGE] [-e EDITION] [-E EXTENSION] [-i ISBN]
                [-d IDENT] [--version] [--debug]

bookwyrm - find books and papers online and download them. When called with no
arguments, bookwyrm prints this screen and exits.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --debug

necessarily inclusive arguments; at least one required:
  -a AUTHOR, --author AUTHOR
  -t TITLE, --title TITLE
  -s SERIE, --serie SERIE
  -p PUBLISHER, --publisher PUBLISHER

exact arguments; optional:
  -y YEAR, --year YEAR
  -l LANGUAGE, --language LANGUAGE
  -e EDITION, --edition EDITION
  -E EXTENSION, --extension EXTENSION
                        filename extension without period, e.g. 'pdf'.
  -i ISBN, --isbn ISBN
  -d IDENT, --ident IDENT
```

## Planned supported sources
### High priority
* Library Genesis
* Bookzz and Booksc
* Sci-Hub
* IRC channels
    - <p>#ebooks on irc-highway</p>
    - etc.
### Medium priority
* Various torrent sides
    - Private (bB, biblotik, etc.)
    - Torrent Project
    - etc.


## Notes
* If an URL for an academic paper is ever needed, [dx.doi.org](http://dx.doi.org) can be used.
* Present results in a menu ála mutt.
    - One result per line in main menu; "n authors title (ext?)"
    - Entering an item takes you to a more detailed menu, where you can download the item.
    - Make program able to download from main menu also.
    - Select multiple items to download all all of them.
