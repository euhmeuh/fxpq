# Final Experience Quest

## The platform game engine and editor  
  
The asset editor and game engine **fxpq** (**F**inal E**xp**erience **Q**uest) is a personal project used to make 2D indie video games in Python. It started as an editor for [Final Experience 2](https://github.com/euhmeuh/fxp2), a 2D multiplayer game.  
It is meant to ease the edition and management of resources in games through a common serializer and a generic XML editor.  

## Setup

 - `pip install -r requirements.txt`

## Run

 - `python3 ./editor.py`

## Run the tests

 - `python3 ./tests.py`

## How it works

The XML format of game files is inspired from WPF, with XML elements corresponding directly to Python classes.  
In the editor, validations are ran live, displaying on the fly error messages if your current file does not pass the data constraints set up in your Python classes.  
The dependency structure of your data files is displayed as a tree in which you can navigate.

## Features

 - Live file validations
 - Direct mapping between Python properties and XML elements
 - Navigation through data dependencies
 - Syntax highlighting
 - Custom data templates
 - Customizable "New entity" window through templates
 - Customizable icons for entities in the navigation tree
 - Python classes are loaded from any Python module/package

## Development miscellaneous

The code follows all PEP8 rules, except the following:
 - E128 - continuation line under-indented for visual indent
 - E309 - expected 1 blank line after class declaration
 - E501 - line too long (> 79 characters)
 - W503 - line break occurred before a binary operator
