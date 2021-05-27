import sys
import os
from PIL import Image, ImageSequence, ImageDraw
from itertools import groupby
import subprocess

def StoreByte(file,value):
	value&=0xff
	file.write(value.to_bytes(1,byteorder='little'))

def StoreByteSwapped(file,value):
	value&=0xff
	a = (value>>4) | ((value&0xf)<<4)
	file.write(a.to_bytes(1,byteorder='little'))


def StoreWord(file,value):
	global binaryData
	value&=0xffff
	file.write(value.to_bytes(2,byteorder='little'))


class Settings:
	def __init__(self):
		self.tile_width = 16
		self.tile_height = 8
		self.meta_width = -1 	# tiles
		self.meta_height = -1	# tiles
		self.outaddress = 0x8000
		self.offset = 0x200
		self.output = "4bpp"
		self.mask = 0xf 
		self.palette = 0
		self.outname = "output"
		self.check_repeats = True
# split into tiles

def Spriteize(name):
	global binaryData,attrib,index,settings
	image = Image.open(name)
	(w, h) = image.size
	tiles = []
	(mw,mh) = (w/settings.tile_width,h/settings.tile_height)

	for ty in range(0,h,settings.tile_height):
		for tx in range(0,w,settings.tile_width):
			blank = []
			index = -1
			palette_index = 0
			# check non flipped
			for py in range(0,settings.tile_height):
				for px in range(0,settings.tile_width):
					p = image.getpixel((tx+px,ty+py))
					blank.append(p & settings.mask)
					# pull palette index if not currently 0 
					if (p&0xf0)>0:
						palette_index = p>>4

			#	check if we have this tile
#			if blank in tiles:
#				index = tiles.index(blank)
#			if (index==-1):
			index = len(tiles)
			tiles.append(blank)

	binaryData = open(settings.outname + ".spr", 'wb')
	for t in tiles:
		for py in range(0,settings.tile_height):
			if settings.output == "8bpp":
				for px in range(0,settings.tile_width):
					b = t[px+(py*settings.tile_width)]
					StoreByte(binaryData,b)	
			if settings.output == "4bpp":
				for px in range(0,settings.tile_width,2):
					a = t[px+(py*settings.tile_width)]
					b = t[(1+px)+(py*settings.tile_width)]
					StoreByte(binaryData,(a<<4) | b)	
	binaryData.close()

	# save palette data
	# nybble swapped and in seperate channels 
	binaryData = open(settings.outname + ".clut", 'wb')
	rgb = image.getpalette()
	for r in range(0,256):
		StoreByteSwapped(binaryData,rgb[(r*3)+0])
	for r in range(0,256):
		StoreByteSwapped(binaryData,rgb[(r*3)+1])
	for r in range(0,256):
		StoreByteSwapped(binaryData,rgb[(r*3)+2])
	binaryData.close()	


def Objectize(name):
	global binaryData,attrib,index,settings,tiles

	# generate long strips to decompress 

	image = Image.open(name)
	(w, h) = image.size
	tiles = []
#	map = []
#	attribs = []	

	(mw,mh) = (w/settings.tile_width,h/settings.tile_height)

	if mw.is_integer()==False:
		print("map width isn't evenly divisible by " + str(settings.tile_width))
	if mh.is_integer()==False:
		print("map height isn't evenly divisible by " + str(settings.tile_height))

	if settings.meta_width==-1:
		settings.meta_width = int(mw) 
		settings.meta_height = int(mh)

	print("map " + str(mw) + "," + str(mh) + " meta " + str(settings.meta_width) + "," + str(settings.meta_height))

	# store the width and height of the map
	binaryData = open(settings.outname + ".info", 'wb')
	StoreWord(binaryData,int(mw))
	StoreWord(binaryData,int(mh))
	binaryData.close()

	mapData = open(settings.outname + ".map","wb")
	attrData = open(settings.outname + ".atr","wb")
	id = 1
	binaryData = bytearray()

	offset = 0 
	offsets = []
	data = []
	lines = []

	uniques = []
	

	for frame in ImageSequence.Iterator(image):		
		buffer = []
		for x in range(0,w):
			for y in range(0,h):
				p = frame.getpixel((x,y))
				buffer.append(p)
		if buffer not in uniques:
			uniques.append(buffer)			
			filename = settings.outname + "_" + hex(id)[2:] + ".str"
			mapData = open("bin/raw.bin","wb")

			print(filename)
			id=id+1
#			rawPixels = open("bin/pic" + "_" + hex(id)[2:] + ".bin","wb")
#			for x in range(0,w):
#				for y in range(0,h):
#					p = frame.getpixel((x,y))
#					StoreByte(rawPixels,p)
#			rawPixels.close()

			for tx in range(0,w,settings.tile_width):
				for y in range(0,h,settings.tile_height):
					for py in range(0,settings.tile_height):
						for px in range(0,settings.tile_width,2):
							p = frame.getpixel((tx+px,py+y)) & settings.mask
							q = frame.getpixel((tx+px+1,py+y)) & settings.mask

							StoreByte(mapData,q<<4 | p)
			mapData.close()

	#		result = subprocess.call("../tools/apultra.exe " + "bin/raw.bin" + " " + filename , shell=False)	
	#		result = subprocess.call("../tools/rle.exe " + "bin/raw.bin" + " " + filename , shell=False)	
	#		result = subprocess.call("../tools/lzsa.exe --prefer-speed " + "bin/raw.bin" + " " + filename , shell=False)	
	#		result = subprocess.call("../tools/c64f.exe " + "bin/raw.bin" + " " + filename , shell=False)	
	#		result = subprocess.call("../tools/zpack.exe " + "bin/raw.bin" + " " + filename , shell=False)	


#			result = subprocess.call("python ../tools/tc_encode.py -r " + "bin/raw.bin" + " " + filename , shell=False)	

#			result = subprocess.call("../tools/packbits.exe " + "bin/raw.bin" + " " + filename , shell=False)	
#			result = subprocess.call("../tools/lzg.exe -9 " + "bin/raw.bin" + " " + filename , shell=False)	
#			result = subprocess.call("../tools/zx0.exe " + "bin/raw.bin" + " " + filename , shell=False)	


			result = subprocess.call("python ../tools/rle.py " + "bin/raw.bin" + " " + filename , shell=False)	
#			result = subprocess.call("../tools/c64f.exe " + "bin/raw.bin" + " " + filename , shell=False)	

			offsets.append(os.stat(filename).st_size)
	#		file = open("bin/raw.bin", "rb")
			file = open(filename, "rb")
			buffer = file.read()


			data.append(buffer)
			file.close()
			result = subprocess.call("rm " + filename , shell=False)	



	mapData = open(settings.outname + ".pak","wb")
#
	baseoffset = 4+(len(offsets)*2)

	binaryData.append(int(mw*2)&0xff)
	binaryData.append(int(mh)&0xff)
	binaryData.append(int(len(offsets)))
	binaryData.append(int(len(offsets))>>8)

	datasize = int((mw * 6) * mh)	# 2 char buffers + 1 attrib buffer   

	base = baseoffset 

	# n frames
#	StoreWord(mapData,len(names))
	base = baseoffset
	for x in offsets:
		binaryData.append(base&0xff)
		binaryData.append(base>>8)
		base=base+x 

	for x in data:
		binaryData+=x

	mapData.write(binaryData)
	mapData.close()
#	print(offsets)
#	print(hex(int(datasize)))

def Tilemize(name):
	global binaryData,attrib,index,settings,tiles

	image = Image.open(name)
	(w, h) = image.size
	tiles = []
#	map = []
#	attribs = []	

	(mw,mh) = (w/settings.tile_width,h/settings.tile_height)


	if mw.is_integer()==False:
		print("map width isn't evenly divisible by " + str(settings.tile_width))
	if mh.is_integer()==False:
		print("map height isn't evenly divisible by " + str(settings.tile_height))

	if settings.meta_width==-1:
		settings.meta_width = int(mw) 
		settings.meta_height = int(mh)

	print("map " + str(mw) + "," + str(mh) + " meta " + str(settings.meta_width) + "," + str(settings.meta_height))

	# store the width and height of the map
	binaryData = open(settings.outname + ".info", 'wb')
	StoreWord(binaryData,int(mw))
	StoreWord(binaryData,int(mh))
	binaryData.close()

	mapData = open(settings.outname + ".map","wb")
	attrData = open(settings.outname + ".atr","wb")
	id = 1
	for frame in ImageSequence.Iterator(image):		
		# chop into tiles
#		print("frame " + str(id))
		id=id+1
		for ty in range(0,h,settings.tile_height*settings.meta_height):
			for tx in range(0,w,settings.tile_width*settings.meta_width):
				# for each type of char 
#				print(str(tx) + "," + (str(ty)))
				map = [0] * (settings.meta_width * settings.meta_height)
				attribs = [0] * (settings.meta_width * settings.meta_height)
				for mtx in range(0,settings.meta_width):
					for mty in range(0,settings.meta_height):
						global index
						blank = []
						blank_x = []
						blank_y = []
						blank_xy = []

						index = -1
						# default attribs for 4bpp
						if settings.output == "4bpp":
							attrib = 0x0f08
						else:
							attrib = 0x0f00

	#					if settings.palette!=0:
	#						attrib= attrib|0x6000

						palette_index = 0
						unique = False
						# check non flipped
						bx = tx + (mtx * settings.tile_width)
						by = ty + (mty * settings.tile_height)
						for py in range(0,settings.tile_height):
							for px in range(0,settings.tile_width):
								p = frame.getpixel((bx+px,by+py))
	#							if (p&0xf)==0xf:
	#								unique = True
	#								p=p&0xf0

								blank.append(p & settings.mask)
								# pull palette index if not currently 0 
								if (p&0xf0)>0:
									palette_index = p>>4
						# set palette attribs
						attrib|=palette_index<<12
						if settings.check_repeats==True:
							#	check if we have this tile
							if blank in tiles:
								index = tiles.index(blank)
							# check x flipped
							if index == -1:
								for py in range(0,settings.tile_height):
									for px in range(0,settings.tile_width):
										p = frame.getpixel((bx+(settings.tile_width-1-px),by+py)) & settings.mask
										blank_x.append(p)
								#	lets see if we have this tile flipped in X
								if blank_x in tiles:
									index = tiles.index(blank_x)
									#	set flipped attributes
									attrib|=1<<6
			
			
							# check y flipped
							if index == -1:
								for py in range(0,settings.tile_height):
									for px in range(0,settings.tile_width):
										p = frame.getpixel((bx+px,(by+(settings.tile_height-1-py)))) & settings.mask
										blank_y.append(p)
								#	lets see if we have this tile flipped in Y
								if blank_y in tiles:
									index = tiles.index(blank_y)
									#	set flipped attributes
									attrib|=1<<7
			
							# check xy flipped
							if index == -1:
								for py in range(0,settings.tile_height):
									for px in range(0,settings.tile_width):
										p = frame.getpixel((bx+(settings.tile_width-1-px),(by+(settings.tile_height-1-py)))) & settings.mask
										blank_xy.append(p)
								#	lets see if we have this tile flipped in X&Y
								if blank_xy in tiles:
									index = tiles.index(blank_xy)
									#	set flipped attributes
									attrib|=1<<6
									attrib|=1<<7
			
	#					#	if we've never seen this one , add it 
						if (index==-1) or (unique==True):
							index = len(tiles)
							tiles.append(blank)
	#
	#
						offset = mtx + (mty*settings.meta_width)
						map[offset] = index + settings.offset
						attribs[offset] = attrib
						#	fill the map data with data we got above

#				s = ""
				for q in map:
#					s = s + hex(q) + ","
					StoreWord(mapData,q)
#				print(s)
				for q in attribs:
					StoreWord(attrData,q)

#				map.append(0x0140)
#				map.append(0x0000)
#				attribs.append(0x0090)
#				attribs.append(0x0000)

		#	save map / screen data

#			map.append(0x0140)
#			attribs.append(0x0010)
#			map.append(0x0000)
#			attribs.append(0x0000)


	print(str(len(tiles)) + " tiles found")

	#	save 4bpp char data ( or 8 bpp )
	binaryData = open(settings.outname + ".chrs", 'wb')
	for t in tiles:
		for py in range(0,settings.tile_height):
			s = "\t"
#									map[offset] = index + settings.offset
			if settings.output == "8bpp":
				for px in range(0,settings.tile_width):
					b = t[px+(py*settings.tile_width)]
					StoreByte(binaryData,b)	
			if settings.output == "4bpp":
				for px in range(0,settings.tile_width,2):
					a = t[px+(py*settings.tile_width)]
					b = t[(1+px)+(py*settings.tile_width)]
					StoreByte(binaryData,(b<<4) | a)
					if a==0:
						s=s + "."
					else:
						s = s + hex(a)[2:].upper()
					if b==0:
						s=s + "."
					else:
						s = s + hex(b)[2:].upper()
#			print(s)

	binaryData.close()

	mapData.close()

	#	save colors / attributes
	attrData.close()

	# save palette data
	# nybble swapped and in seperate channels 
	binaryData = open(settings.outname + ".clut", 'wb')
	rgb = image.getpalette()
	for r in range(0,256):
		StoreByteSwapped(binaryData,rgb[(r*3)+0])
	for r in range(0,256):
		StoreByteSwapped(binaryData,rgb[(r*3)+1])
	for r in range(0,256):
		StoreByteSwapped(binaryData,rgb[(r*3)+2])

	binaryData.close()	

def main():
	global binaryData,attrib,index,settings
	settings = Settings()

	for a in range(1,len(sys.argv)):
		arg = sys.argv[a]
		print(arg)

		if "-b4" in arg:
			settings.tile_width = 16
			settings.output = "4bpp"
			settings.mask = 0xf
		elif "-b8" in arg:
			settings.tile_width = 8
			settings.output = "8bpp"
			settings.mask = 0xff
		elif arg.startswith("-m="):
			settings.outaddress = int(arg[3:],16)
			settings.offset = settings.outaddress//64
		elif arg.startswith("-o="):
			settings.outname = arg[3:]
		elif arg.startswith("-t="):
			name = arg[3:]
			settings.check_repeats = True
			Tilemize(name)
		elif arg.startswith("-tn="):
			name = arg[4:]
			settings.check_repeats = False
			Tilemize(name)
		elif arg.startswith("-p="):
			name = arg[3:]
			Objectize(name)
		elif arg.startswith("-s="):
			settings.tile_height = 128
			name = arg[3:]
			Spriteize(name)
		elif arg.startswith("-mt="):
			settings.meta_width = 8 
			settings.meta_height = 32
			settings.tile_height = 8
			settings.check_repeats = False
			name = arg[4:]
			Tilemize(name)



if __name__ == '__main__':
   main()


