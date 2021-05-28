

rem python tools\tilemizer.py -m=8000 -b4 -o=bin\16color -t=exampledata\grid.bmp
tools\bmp2m65.exe -m -b 8000 -o bin\16color exampledata\grid.bmp

millfork-0.3.28\millfork.exe -t mega65_small -fsource-in-asm -s -g -i include m65.16color.mfk -o bin\16color
tools\exomizer sfx basic -t65 bin\16color.prg -o bin\16color.x.prg 

