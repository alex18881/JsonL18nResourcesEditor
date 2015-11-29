Json L18n Resources Editor
================
Description
---
This package allows to edit localization/internationalization resources stored in JSON files. For example:
resources.json
resources.en-us.json
resources.en-gb.json

![Screenshot](http://i.imgur.com/eYPSpFw.png)

Sublime Text 3 plugin for editing localization internationalization resources JSON

Installation
---
  - Using [Package Control](https://packagecontrol.io/) Ctrl+Shift+P -> "Install Package" then type JsonL18nResourcesEditor and press enter
  - Clone the [repository](https://github.com/alex18881/JsonL18nResourcesEditor) or download ZIP and extract to the JsonL18nResourcesEditor directory in your Sublime 'Packages' folder ( menu "Preferences"->"Browse Packages" )

Usage
---

![Screenshot](http://i.imgur.com/tfF6IOR.png)

  - Right click on one of any file from sequence of JSON resources files in sidebar. ( Sequence of JSON resources is a number of JSON files located in the same directory with similar names i.e. resources.json, resources.en-us.json, resources.en-gb.json )
  - Select "Edit L18n resource" in context menu.
  - Edit resources as JSON strings in opened window.

Note that each value should be a proper single line JSON string. All special chars must be escaped.
Resulting saved files will be pretty-print-formatted.

P.S.
---
Please leave comments [here]()
Feel free to post [issues](https://github.com/alex18881/JsonL18nResourcesEditor/issues)

Changes in 1.1.0:
---
- added settings
- added tab content command

Changes in 1.0.0:
---
- fixed new row creation
- fixed small bugs