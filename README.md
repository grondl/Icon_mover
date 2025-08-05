I regularly have icons not show up on my dual screen Linux Mint Mate setup.  With the help of Chatgpt I produced this helper program that when run shows
the layout of my 2 screens and where the icons are positionned.  If an icon is outside the visible screen area I can now drag it back to the visible area.

Misplaced icons sometimes happens when I create a new icon or when I play around with the resolution and positionning of the screens.

The program is python and it uses the GTK module for the graphic user inteface (GUI).  
It also calls 2 system programs that shold be available by default in a Linux Mint Mate installation ...
It uses the gio program to get the current icon positions and reposition the dragged icon.  
It also makes caja quit knowing it will restart itself,  this refreshes the physical screens with the new icon position.
