📜 Bookwyrm
---
bookwyrm is a TUI-based program written in C++17 which, given some input data,
searches for matching ebooks and academic papers on various sources.
During runtime, all found items are presented in a menu,
where you can choose which items you want to download.

An item can be viewed for details, which will be fetched from some database (unless the source itself holds enough data), such as the Open Library or WorldCat.
A screen holding logs from worker threads is available by pressing TAB. All unread logs are printed to std{out,err} upon program termination.

For example, one might run bookwyrm as follows:

    bookwyrm --author "Naomi Novik" --series Temeraire --year >=2015

Here is an (outdated) video of bookwyrm in action:
[![asciicast](https://asciinema.org/a/9kRtmSvVupD6PsUdtBKQ3vZaD.png)](https://asciinema.org/a/9kRtmSvVupD6PsUdtBKQ3vZaD)

Sources are written as scripts which run in their own worker threads.
Some scripts are available upstream, but you can also write your own into `~/.config/bookwyrm/sources/`. Currently, only Python scripts are supported, but LUA is being considered.
A script may need data from the user (e.g. login credentials); this can be written into `~/.config/bookwyrm/config.yaml`.

Aside from a C++17-compliant compiler and CMake, bookwyrm also depends on a few libraries:
* **fmt**,        for a few print-outs and since spdlog depends on it;
* spdlog,         for logging warnings/errors/etc. to the user;
* termbox,        for the TUI;
* **pybind11**,   for interfacing with Python, and
* **fuzzywuzzy**, for fuzzily matching found items with what's wanted.

All libraries that do not use a bold font are non-essential and may be subject to removal later in development. All dependencies are submoduled in `lib/`.

bookwyrm is still in the early development stage, so nothing is set in stone. A v1.0.0 release is planned for early Q1 2018.

If you have any insights, questions, or wish to contribute,
create a PR/issue on GitHub at <https://github.com/Tmplt/bookwyrm>.
You can also contact me via email at `echo "dG1wbHRAZHJhZ29ucy5yb2Nrcwo=" | base64 -d`.

bookwyrm is licensed under the GPLv3+.
