# Inspiration Pad Pro (Extended)
Since Inspiration Pad Pro is going on a decade without an update, here we go! Send me your suggestions, or fork the project and add your own ideas to it.

This project is endorsed by NBOS Software (thanks Ed!).
For the original NBOS Software program, go to https://www.nbos.com/products/inspiration-pad-pro

License: GNU GPLv3 (See LICENSE)

## Needing an updated IPP Program
Inspiration Pad Pro development stopped with IPP 3.0 nearly a decade ago. Lots of ideas have been floated on the forums, but no actual development has taken place on IPP 4.

This started as a Python experiment in recursion, and developed into what you see now. I am slowly implementing the older tags used in IPP 3.0, updating the script syntax where needed (both to simplify the code and make it easier to parse recursively).
The biggest issue you will run into using this program is that due to updated syntax, it does not fully work with older IPP scripts. I have not decided whether I am going to implement reverse-compatibility, or only work to parse the updated syntax.

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

## Updated Syntax
- Change sub-table pick syntax from [|option1|option2] to [|option1|option2|]
- Implode uses a quote delimited modifier to determine the implosion characters to use. Examples: [@5 Table >> implode "<br>"] and [@5 Table >> implode ", "]

### Mostly Complete
- Support for floating-point and integer math [currently works in conjunction to dice rolls only]
- Simple HTML Support (this turned out a lot more complicated than I originally anticipated) [simple HTML h1,h2,h3,b,i,u,p,br,hr,li are working]

### Future Goals
- Add new logic syntax to IPP for better and easier random scripts
  - Add multiple tables picks ! as modifiers
  - Sort function
  - Text options for upper, lower, and proper
  - Add a/an English logic
- Sub-table Interactive Rerolls (click on a particular part of the output to reroll just that section.)
- Add HTML support
  - Table Output
  - Images
  - CSS Support?
- Export Options
  - Export to Printer
  - Export to PNG
  - Export to PDF

## Current Development Screenshots
![Imgur](https://imgur.com/WVnWNea.png)
The current editing window allows for seamless script design and generation side-by-side. There is no need to save in-between editing and generating. You only need to save when you are happy with the script. Save files are in .txt format.
![Imgur](https://imgur.com/EpcKsa7.png)
Using the drop-down menu at the top, you can select which Table in the script to run from. The program defaults to the first table on load, but you can manually run the program at any of the available tables in the script. Use the Scan/Refresh button to update the dropdown menu if you add more tables to the script editor and it doesn't immediately show them in the menu.
