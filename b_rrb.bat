

rem python tools\tilemizer.py -m=8000 -b4 -o=bin\16color -t=exampledata\grid.bmp
tools\bmp2m65.exe -m -b 8000 -o bin\ddp exampledata\ddp.bmp
tools\bmp2m65.exe -r -b 6000 -o bin\ship exampledata\ship.bmp

millfork-0.3.28\millfork.exe -t mega65_small -fsource-in-asm -s -g -i include m65.rrb.mfk -o bin\rrb
tools\exomizer sfx basic -t65 bin\rrb.prg -o bin\rrb.x.prg 

