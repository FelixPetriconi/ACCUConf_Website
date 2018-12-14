![Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png)

# ACCU Conference Website

## Introduction

This repository contains the source for the [ACCU Conference website](http://conference.accu.org)
(http://conference.accu.org). The content is managed as a Nikola website.

## Getting Started

The following tools are needed:
- [Git](https://git-scm.com/) – required to clone your GitHub fork of the repository, and to push changes to
  your fork on GitHub ready to submit pull requests on GitHub.
- [Python](https://www.python.org) – required to run Nikola. You should install Python 3, not Python 2. You
  will most likely need to ensure the application pip3 is installed so as to install Nikola.
- [Nikola](https://getnikola.com/) – required to build the website. This is a Python application, hence
  requiring Python.
- [AsciiDoctor](https://asciidoctor.org) required for Nikola to render individual source pages.

Linux and UNIX distributions may well allow installation of these using package management. For example on
Debian Sid, there are packages for git, python3, python3-pip, and asciidoctor, but there is no package for
nikola. macOS has Homebrew which like Debian Sid allows git, python3 (includes pip3), and asciidoctor to be
installed but there is no formula for nikola. For Windows, there are installers for Git
(https://git-scm.com/download/win or https://gitforwindows.org/) and Python
(https://www.python.org/downloads/windows/); for AsciiDoctor you will need to install Ruby and Gem, and then
install the AsciiDoctor gem https://asciidoctor.org/docs/install-toolchain/.

If there is a package for Nikola on your platform feel free to use that. It seems most likely though that
most people will be installing Nikola using pip3 and the PyPI package repository.

If you are installing Nikola using pip3, you may want to use a virtual environment, but it is likely easiest
to install a user specific version. The file `requirements.txt` contains a list of the things needed to
build the website. So if you need to set up your environment, the command:

    pip3 install --user --upgrade -r requirements.txt

is a good way of setting up per-user packages initially, and also of updating – which should be done
regularly. This will put the `nikola` executable somewhere sensible (this is `$HOME/.local/bin` on Debian
Sid) but you need to make sure that the installation directory of this executable is in your `PATH`.

With that done:

    nikola build

should build the website in ./output.

## Adding Material

By convention all source is AsciiDoc, even though Markdown or ReStructuredText are possible. So only
AsciiDoc please.

There are two sorts of material, posts and stories. Posts are blog entries, and will appear on the front
page. Stories are free standing pages, that will have to be linked to from blog entries, the menu, or
somewhere on the front page.

The Code of Conduct and various pages from previous years conferences are stories.

Posts, aka blog entries, have a source file name consisting of the date of creation in ISO8601 format
followed by an underscore followed by the title in camel case with no spaces, with the `adoc` extension.


## The Licence

All material in this repository is licensed under
[Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](http://creativecommons.org/licenses/by-nd-nc/4.0/).
