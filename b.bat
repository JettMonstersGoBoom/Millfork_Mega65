

rem python tools\tilemizer.py -m=6000 -b4 -o=data\ship -p=resources\ship.bmp
python tools\tilemizer.py -m=8000 -b4 -o=bin\16color -t=exampledata\grid.bmp
millfork-0.3.28\millfork.exe -t mega65_small -fsource-in-asm -s -g -i include mega.dmatest.mfk -o bin\dmatest
millfork-0.3.28\millfork.exe -t mega65_small -fsource-in-asm -s -g -i include mega.16color.mfk -o bin\16color

