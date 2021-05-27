millfork-0.3.28\millfork.exe -t mega65_multifile -fsource-in-asm -s -g -i include mega.disk.mfk -o bin\disk
tools\c1541.exe -format "multifile,11" d81 multifile.d81 -write bin\disk.prg start -write bin\disk.extra.prg extra

