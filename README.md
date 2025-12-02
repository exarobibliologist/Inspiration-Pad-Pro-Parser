# Inspiration Pad Pro Interpreter (Extended)
Since Inspiration Pad Pro is going on a decade without an update, here we go! Send me your suggestions, or fork the project and add your own ideas to it.

For the original NBOS Software program, go to https://www.nbos.com/products/inspiration-pad-pro

This project is not endorsed by NBOS Software (although we would love to be).

License: GNU GPLv3 (See LICENSE)

## Needing an updated IPP Program
Inspiration Pad Pro development stopped with IPP 3.0 nearly a decade ago, leaving the program with several odd limitations. Lots of ideas have been floated on the forums, but no actual development has taken place on IPP 4.

This Python script would like to eventually become the stand-in for Inspiration Pad Pro 4.0, but there's still a long way to go... Here's the timeline.

## TIMELINE
### Tasks Complete
- Create window that allows editing and generation to happen at the same time
- Choose what Table to start generation on (not just the first table like IPP 3)
- Read existing IPP script files
- Saving/loading
- Zebra-striped lines for easy reading
- Support for numerical ranges without needing dice rolls
- Change sub-table pick syntax from [|option1|option2] to [|option1|option2|]
- Added multiple table picks using @ followed by a number, as in [@5 table]
- Added clear seperation lines between generations in the Output Pane

### Mostly Complete
- Support for floating-point and integer math [currently works in conjunction to dice rolls only]
- Simple HTML Support (this turned out a lot more complicated than I originally anticipated) [simple HTML h1,h2,h3,b,i,u,p,br,hr,li are working]


### Future Goals
- Add new logic syntax to IPP for better and easier random scripts
  - Add multiple tables picks ! as modifiers
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
