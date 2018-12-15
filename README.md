![Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png)

# ACCU Conference Website

## Introduction

This repository contains the source for the [ACCU Conference website](http://conference.accu.org)
(http://conference.accu.org). The content is managed as a Nikola website.

## Getting Started

The following tools are needed to build the website locally:
- [Git](https://git-scm.com/) – required to clone your GitHub fork of the repository, and to push changes to
  your fork on GitHub ready to submit pull requests on GitHub.
- [Python 3](https://www.python.org) – required to run Nikola. You should install Python 3, not Python 2. You
  will most likely need to ensure the application pip3 is installed so as to install Nikola and its dependencies.
- [Nikola](https://getnikola.com/) – required to build the website. This is a Python application, hence
  requiring Python 3.
- [AsciiDoctor](https://asciidoctor.org) required for Nikola to render individual source pages.

Linux and UNIX distributions may well allow installation of these using package management. For example on
Debian Sid, there are packages for git, python3, python3-pip, and asciidoctor, but there is no package for
nikola. macOS has Homebrew which like Debian Sid allows git, python3 (includes pip3), and asciidoctor to be
installed but there is no formula for nikola – MacPorts will certainly have a similar situation. For
Windows, there are installers for Git (https://git-scm.com/download/win or https://gitforwindows.org/) and
Python (https://www.python.org/downloads/windows/); for AsciiDoctor you will need to install Ruby and Gem,
and then install the AsciiDoctor gem https://asciidoctor.org/docs/install-toolchain/.

If there is a package for Nikola on your platform feel free to use that. It seems most likely though that
most people will be installing Nikola using pip3 and the PyPI package repository.

If you are installing Nikola using pip3, you may want to use a Python virtual environment. However the
alternative of creating a user specific install using the system Python 3 seems to be a very good way of
installing Nikola. This avoids some of the hassles of using a virtual environment in this sort of
context.

The file `requirements.txt` contains a list of the Python 3 packages needed to build the website. The command:

    pip3 install --user --upgrade -r requirements.txt

is a good way of setting up per-user packages initially, and also of updating the installation – which should be done
regularly. This will put the `nikola` executable somewhere sensible (this is `$HOME/.local/bin` on Debian
Sid). You need to make sure that the installation directory of this executable is in your `PATH` so that you
can run the `nikola` command from a command line.

With that done:

    nikola build

should build the website in ./output. However,… due to an issue within Nikola – that has been reported and
investigated, and a decision made it cannot be fixed – you will have to run the command again to get a
proper build. This is only needed from a clean state: once you have a build, any changes you make you will
only need to run Nikola once to update the build, but from a clean state you must run Nikola at least
twice. The way to know you have a complete build is to run Nikola and there are no changes. For example:

    |> nikola build
    Scanning posts......done!
    |>

Loading ./output/index.html will now show the built website and allow for navigation around it. For example:

    |> epiphany output/index.html &
    |>

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
[Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nd-nc/4.0/)
![Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png)
.
