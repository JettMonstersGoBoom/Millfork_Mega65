# Millfork_Mega65
repo for Mega65 &amp; Millfork &amp; Shallan's compo base


b.bat and it's variants b_16color.bat etc. are used to build the demos

r.bat and it's variants r_16color.bat etc. are used to launch the demo on mega65 or nexys.

you may need to adjust to suit

#

mega.dmatest.mfk is hello world 

# 16 colors


mega.16color.mfk uses DMA and sets up 16 color mode 

# RRB 

mega.rrb.mfk DMA 16 color mode and working RRB objects


# tools

tools\bmp2m65 added as a stand alone tool to convert bmp to m65 format tiles and rrb strips

-b 8000 
sets base tile address to $8000 

-o basename 
output is 
basename.chrs 
basename.clut 
basename.map 
basename.atr

-m 
output a traditional tilemap 16x8 pixels 

-r 
output an RRB object, which is split into 16 pixel * height strips

plus 2 blank tiles above and below the image for RRB Y offset 

# extras

there is an older tilemizer.py script that is no longer supported. but left for reference

you will need python 3 and pillow installed for the image script to work. 









