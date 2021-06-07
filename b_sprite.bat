
tools\bmp2m65 -s -o bin\shipsprite exampledata\sprite.bmp
java -jar millfork-0.3.28\millfork.jar -t mega65_small -fsource-in-asm -s -g -i include m65.sprites.mfk -o bin\spritetest

