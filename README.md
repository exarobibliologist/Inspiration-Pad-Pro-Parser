# Inspiration Pad Pro (Extended)
Since Inspiration Pad Pro is going on a decade without an update, here we go! Send me your suggestions, or fork the project and add your own ideas to it.

This project is endorsed by NBOS Software (thanks Ed!).
For the original NBOS Software program, go to https://www.nbos.com/products/inspiration-pad-pro

License: GNU GPL-3.0 (See LICENSE)

## Needing an updated IPP Program
Inspiration Pad Pro development stopped with IPP 3.0 nearly a decade ago. Lots of ideas have been floated on the forums, but no actual development has taken place on IPP 4.
This started as a Python experiment in recursion, and developed into what you see now. I am slowly implementing the logic used in IPP 3.0, and occasionally updating the logic syntax where needed (both to simplify the code and make it easier to parse recursively).

The biggest issue you will run into using this program is that due to updated syntax, it does not fully work with older IPP scripts. Once I am finished with the v4 logic syntax, I am going to write a v3 logic file to handle older and newer scripts.

## Pivoting in a New Direction
I have always intended that this be an extensible program that people can modify the logic of themselves, but as I continued programming the original Inspiration_Pad_Pro_Parser I kind of lost my focus. Every new rule that I added to the original program required massive changes to multiple parts of the script, and the complications snowballed.
I am attempting to pivot back to my original focus.

The new RPG Pad Pro features ruleset files. These files contain the logic functions that the program uses on the table input to generate the output. They are self-contained, so changes in the logic files don't create massive changes in other scripts that the program uses.

All of these logic files are written in Python.
The \v4 Ruleset\ folder is the current logic system I am developing, but it should be much easier to redevelop the v3 logic afterwards and make this a program that can parse old IPP tables, new v4 tables, and even custom logic files that anyone can write.

Since the program is modular, anyone can write their own logic files or modify existing files to better suit their needs. To add your own custom logic to the program, create a new folder in \Rules\ and add your Python logic files there. You can also copy the files from the \v4 Ruleset\ folder to a new folder and modify them for your needs.

## Looking to the Future
This Python script would like to eventually become the stand-in for Inspiration Pad Pro 4.0, but there's still a long way to go... Here's the timeline.

## TIMELINE
### Tasks Complete
- Create window that allows editing and generation to happen at the same time
- Choose what Table to start generation on (not just the first table like IPP 3)
- Saving/loading
- Zebra-striped lines for easy reading
- Support for numerical ranges without needing dice rolls
- Added multiple table picks using @ followed by a number, as in [@5 table]
- Added clear seperation lines between generations in the Output Pane
- Implode function to separate multiple generations of a table
- Sort function (alphabetically, and numerically) now works perfectly! This feature implements a natural sorting function that strips any HTML from a list item before evaluating the sort key. This fixes a long-standing bug present in the original Inspiration Pad Pro program where a list containing numbers would sort incorrectly (e.g., in the old system, 10 would be placed before 2 because it was sorting by the first digit).

## Updated Syntax
- Change sub-table pick syntax from [|option1|option2] to [|option1|option2|]
- Implode uses a quote delimited modifier to determine the implosion characters to use. Examples: [@5 Table >> implode "<br>"] and [@5 Table >> implode ", "]
- Support for floating-point and integer math
- Support for floating-point and integer math [currently works in conjunction to dice rolls only]
- Full support for HTML!!! Yes, FULL!! You could probably even use CSS if you wanted to!
  - simple HTML implemented for when "Generate >>" and using Simple Output [h1,h2,h3,b,i,u,p,br,hr,li]
  - full HTML supported, with tables, and images when using "Generate to Browser"
- Text options for upper, lower, and proper
- Add a/an English switch logic
- {variable} assignment
- Logic Systems added for if/then/else, ifnot/then/else, while/do, whilenot/do
- [!Deck] and [!5 Deck] picks
  - Reset: to reset tables for additional deck picks


### Mostly Complete
  - Table Output [table, td, tr] [implemented but currently broken in output viewer]

### Future Goals
- Add new logic syntax to IPP for better and easier random scripts
  - Set: variables
  - Define: variables
  - \Escape\ logic
  - Headers and Footers
- Sub-table Interactive Rerolls (click on a particular part of the output to reroll just that section.)
- Custom CSS Support?
- Export Options
  - Export to Printer
  - Export to PNG
  - Export to PDF

## Current Development Screenshots
![Imgur](https://imgur.com/JIq1jlK.png)
The current editing window allows for seamless script design and generation side-by-side. There is no need to save in-between editing and generating. You only need to save when you are happy with the script. Save files are in .txt format.
![Imgur](https://imgur.com/617Sjds.png)
With our math and random pick suite, you can generate tables to make any fantasy world come to life!
![Imgur](https://imgur.com/kcTyfzQ.png)
Using the drop-down menu at the top, you can select which Table in the script to run from. The program defaults to the first table on load, but you can manually run the program at any of the available tables in the script. Use the Scan/Refresh button to update the dropdown menu if you add more tables to the script editor and it doesn't immediately show them in the menu.
