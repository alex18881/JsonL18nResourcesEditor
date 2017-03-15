# Json L18n Resources Editor
_Sublime Text 3 plugin for editing localization internationalization resources JSON_. 
(the package title says L18n which kind of mixing 2 terms l10n and i18n.)

## Description

This package allows to edit localization/internationalization resources stored in JSON files. For example:
resources.json
resources.en-us.json
resources.en-gb.json

![Editor window](http://i.imgur.com/eYPSpFw.png)

## Installation

  - Using [Package Control](https://packagecontrol.io/) Ctrl+Shift+P -> "Install Package" then type JsonL18nResourcesEditor and press enter
  - Clone the [repository](https://github.com/alex18881/JsonL18nResourcesEditor) or download ZIP and extract to the JsonL18nResourcesEditor directory in your Sublime 'Packages' folder ( menu "Preferences"->"Browse Packages" )

## Usage

![Sidebar context menu](http://i.imgur.com/tfF6IOR.png)
![Tab context menu](http://i.imgur.com/CMJD4Cr.png)

  - Right click on one of any file from sequence of JSON resources files in sidebar or in its tab if it's open and is currently selected. ( Sequence of JSON resources is a number of JSON files located in the same directory with similar names i.e. resources.json, resources.en-us.json, resources.en-gb.json )
  - Select "Edit L18n resource" in context menu.
  - Edit resources as JSON strings in opened window.
  - Use TAB and SHIFT+TAB to shitch between languages

![Multiple rows strings editor](http://i.imgur.com/M458Ylx.png)

If you need to make a multiline string which should contain "\n" symbols just press _CTRL+Enter_ to enter into multiline editor there to make new line use SHIFT+Enter, and to apply changes just hit _Enter_

*Note that each value should be a proper single line JSON string. All special chars must be escaped.
Resulting saved files will be pretty-print-formatted.*

## P.S.

Feel free to post [issues](https://github.com/alex18881/JsonL18nResourcesEditor/issues)

## Changes
### 1.2.1 - 1.2.3:
- bugfix

### 1.2.0:
- added jump to next lang resource by tab press and previous by shift+tab
- added multiline strings editing by CTRL+Enter
- row adding fixed

### 1.1.1:
- bugfix

### 1.1.0:
- added settings
- added tab content command

### 1.0.0:
- fixed new row creation
- fixed small bugs
