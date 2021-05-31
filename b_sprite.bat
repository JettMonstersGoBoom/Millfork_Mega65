
tools\bmp2m65.exe -s -o bin\shipsprite exampledata\sprite.bmp
millfork-0.3.28\millfork.exe -t mega65_small -fsource-in-asm -s -g -i include m65.sprites.mfk -o bin\spritetest

