# PDM reader

Interactive reader for [PowerDesigner](https://www.sap.com/products/powerdesigner-data-modeling-tools.html) PDM files.

Features:

* View/search tables
* Vew table definition
* Generate DDL for various databases (currently MySQL and Oracle supported)
* Generate Java entity definition
* Support command history

## Requirement

* Python 3.7+

This tool only makes use of Python standard libraries.

## Installation

```bash
# root or administrator permission may be required
pip install pdmreader
```

If you want to try some unreleased features, or customize the tool yourself, clone the repository and install it in development mode:

```bash
git clone https://github.com/bianjp/pdmreader.git
cd pdmreader
# root or administrator permission may be required 
python setup.py development
```

## Usage

```bash
pdmreader PATH_TO_PDM_FILE
```

This will start an interactive "shell" which you can type commands.

Type `help` to show available commands.

Currently supported commands:

    COMMAND                       DESCRIPTION
    --------------------------------------------------------------------------------
    help                          Print help
    t                             Toggle horizontal/vertical output. Default horizontal
    tables                        Show tables
    tables PATTERN                Show tables matching the given shell-style glob
    seq                           Show sequences
    seq PATTERN                   Show sequences matching the given shell-style glob
    table TABLE                   Show definitions of the given table
    mysql TABLE                   Generate MySQL DDL for creating the given table
    oracle TABLE                  Generate Oracle DDL for creating the given table
    java TABLE                    Generate Java entity definition for the given table
    exit, Ctrl + D                Exit

## License

This project is licensed under the terms of the MIT license.
