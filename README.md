![Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png)

# ACCU Conference Website

## Introduction

This repository contains the source for the [ACCU Conference website](http://conference.accu.org)
(http://conference.accu.org). The content is managed as a Nikola website.

## Getting Started

Git and [Nikola](https://getnikola.com/) are needed, Git to clone this repository and Nikola to build the website.

Most operating system distributions package Git. If yours doesn't have Git you will need to install it via
the most idiomatic way for your operating system.

Many operating system distributions package Nikola (some only the Python 2 version though :-( If there is
not a suitable package then creating a virtualenv and installing Nikola from PyPI using pip works well, as
does using per-user installed packages – Python 3 being the most senble choice of Python obviously. The file
`requirements.txt` contains a list of the things needed to build the website. So if you need to set up your
environment, the command:

    pip3 install --user --upgrade -r requirements.txt

is a good way of setting up per-user packages initially, but also of updating – which should be done
regularly. This will put the `nikola` executable in `$HOME/.local/bin` so you need to make sure that path is
in your `PATH`.

With that done:

    nikola build

should build the website in ./output.

## Adding Material

By convention all source is Asciidoc, even though Markdown or ReStructuredText are possible. So only
Asciidoc please.

There are two sorts of material, posts and stories. Posts are blog entries, and will appear on the front
page. Stories are free standing pages, that will have to be linked to from blog entries, the menu, or
somewhere on the front page.

The Code of Conduct and various pages from previous years conferences are stories.

Posts, aka blog entries, have a source file name consisting of the date of creation in ISO8601 format
followed by an underscore followed by the title in camel case with no spaces, with the `adoc` extension.


## The Licence

All material in this repository is licensed under
[Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](http://creativecommons.org/licenses/by-nd-nc/4.0/).
