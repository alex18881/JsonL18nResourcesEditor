Json L18n Resources Editor
================
Descrition
---
This package allows to edit localization/internationalization resources stored in JSON files. For example:
resources.json
resources.en-us.json
resources.en-gb.json

![Screenshot](http://i.imgur.com/eYPSpFw.png)

Sublime Text 3 plugin for editing localization internatioanlization resources JSON

Installation
---
  - Using [Package Control](https://packagecontrol.io/) Ctrl+Shift+P -> "Install Package" then type JsonL18nResourcesEditor and press enter
  - Clone or download ZIP and extract to the JsonL18nResourcesEditor directory in your Sublime 'Packages' folder ( menu "Preferences"->"Browse Packages" )

Usage
---

![Screenshot](http://i.imgur.com/tfF6IOR.png)

  - Right click on one of any file from sequence of JSON resources files in sidebar. ( Sequence of JSON resources is a number of JSON files located in the same directory with similar names ie resources.json, resources.en-us.json, resources.en-gb.json )
  - Select "Edit L18n resource" in context menu.
  - Edit ersources as JSON strings in opened window.

Note that each value should be a proper single line JSON string. All special chars must be escaped.
Resulting saved files will be pretty-print-formatted.


Changes in 1.0.0:
---
- fixed new row creation
- fixed small bugs
