VerySeriousButton-vsbutil
=========================

"Service utility" for the Very Serious Button (https://www.indiegogo.com/projects/very-serious-button).

This code was built for testing and initial programming of Very Serious Buttons during production. It is being provided as a tool for advanced users and a reference to illustrate how the HID configuration interface works.

For normal use you might prefer the official, point-and-click [VerySeriousSetup](https://github.com/g-nospace-c/VerySeriousButton-VerySeriousSetup/) application.

## Requires:
* Reasonably recent Windows, Linux or Mac OS X
* Python [hidapi](https://pypi.org/project/hidapi/) package

## Installing:
Activate a virtual environment with your tool of choice and run `pip install .` from this top directory.

Alternatively, use [pipx](https://github.com/pypa/pipx) to install in a dedicated environment in one step:
```
pipx install "git+https://github.com/g-nospace-c/VerySeriousButton-vsbutil.git"
```

To run `vsbutil` in place without installing the package, run `python vsbutil.py` here.

## Usage:
See online help (`vsbutil --help`) for available commands and options.

## Examples:
    vsbutil setjoy
    vsbutil saveconfig

    vsbutil setkey ctrl+c
    vsbutil saveconfig

    vsbutil setkeys shift+h e l l o comma space w o r l d shift+1

## Notes:
Configuration changes made by the "setjoy" or "setkey" commands are applied in RAM and will not persist across a reset unless you explicitly call the "saveconfig" command afterward. However, the "setkeys" commits changes to nonvolatile storage immediately.

## Author:
GC \<gc@grenlabs.com\>
