#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "dmt.h"

#define log(M, ...) fprintf(stdout, "\33[32mINFO\33[39m  " M "  \33[90m at %s (%d) \33[39m\n", ##__VA_ARGS__, __func__, __LINE__)

#include "stretchy_buffer.h"

#pragma pack(1)


FILE *chrs_fp,*map_fp,*atr_fp;
uint16_t tile_offset = 0;
uint32_t vram_location = 0;

typedef struct
{
	uint16_t magic;
	uint32_t fileSize;
	uint32_t reserved0;
	uint32_t bitmapDataOffset;
	uint32_t bitmapHeaderSize;
	uint32_t width;
	uint32_t height;
	uint16_t planes;
	uint16_t bitsPerPixel;
	uint32_t compression;
	uint32_t bitmapDataSize;
	uint32_t hRes;
	uint32_t vRes;
	uint32_t colors;
	uint32_t importantColors;
} BMPHeader_t;
#define SWAP_UINT8(x) (((x&0xf0) >> 4) | ((x&0xf0)))

uint8_t *bmp_buffer;
uint32_t bmp_width,bmp_height;
unsigned char bmp_palette[256][3];		/* palette */

int bmp_load(char *name)
{
	BMPHeader_t header;
	int i;
	FILE *      pFile      = NULL;
	/* no it's a new file - ok let's prepare loading */
	if (bmp_buffer)
		dmt_free(bmp_buffer);
	bmp_buffer = NULL;

	/* open the file */
	if ((pFile = fopen(name, "rb")) == NULL) {
		log("Can not open file!");
		goto errorCleanup;
	}

	fread(&header,1,sizeof(BMPHeader_t),pFile);

	/* adjust picture size to 8-pixel character boundaries */
	bmp_width = (header.width + 7) & ~7;
	bmp_height = (header.height + 7) & ~7;

	/* check size range */
	if ((bmp_width > 16384) || (bmp_height > 4096)) {
		log("Picture size too big, max. 16384x4096!");
		goto errorCleanup;
	}
	if ((bmp_width < 16) || (bmp_height < 16)) {
		log("Picture size too small, min. 16x16!");
		goto errorCleanup;
	}

	/* malloc a buffer */
	bmp_buffer = dmt_malloc(bmp_width * (bmp_height+1));
	if (bmp_buffer == NULL) {
		log("Can not load file, not enough memory!");
		goto errorCleanup;
	}
	for (i=0;i<header.colors;i++)
	{
		fread(&bmp_palette[i][2],1,1,pFile);
		fread(&bmp_palette[i][1],1,1,pFile);
		fread(&bmp_palette[i][0],1,1,pFile);
		fseek(pFile,1,SEEK_CUR);
	}
	for (i = header.colors; i < 256; i += 1) {
		bmp_palette[i][0] = 0;
		bmp_palette[i][1] = 0;
		bmp_palette[i][2] = 0;
	}

	if (header.bitsPerPixel==4)
	{
		for (uint32_t y=0;y<bmp_height;y++)
		{
			for (uint32_t x=0;x<bmp_width;x+=2)
			{
				uint8_t byte;
				fread(&byte,1,1,pFile);
				bmp_buffer[x+(((header.height-1-y))*header.width)]=byte>>4;
				bmp_buffer[1+x+(((header.height-1-y))*header.width)]=byte&0xf;
			}
		}
	}
	else 
	{
		fseek(pFile,header.bitmapDataOffset,SEEK_SET);
		for (uint32_t y=0;y<bmp_height;y++)
		{
			for (uint32_t x=0;x<bmp_width;x++)
			{
				uint8_t byte;
				fread(&byte,1,1,pFile);
				bmp_buffer[x+(((header.height-1-y))*header.width)]=byte;
			}
		}
	}
	fclose(pFile);
	return (1);

errorCleanup:
	if (pFile)
		fclose(pFile);
	return (0);
}

#define TILE_W 16 
#define TILE_H 8 

typedef struct 
{
	uint32_t clut:8;
	uint32_t xflip:1;
	uint32_t yflip:1;
	uint32_t index:16;
} TILE_ATTRIB;

typedef struct 
{
	int				height;
	uint32_t 	crc;
	int 			xflip;
	uint32_t	vram_location;
	uint8_t 	*bytes;
} TILE;

TILE **tiles;

TILE_ATTRIB *tile_map;

uint8_t get_pixel(int x,int y)
{
	if ((x>bmp_width) || (y>bmp_height) || (x<0) || (y<0)) 
		return 0;
	return (bmp_buffer[x+(y*bmp_width)]);
}

void get_tile_4bpp(int x,int y,int *clut,TILE *tile)
{
	tile->crc = 0;
	if (clut!=NULL)
		*clut = 0;

	for (int py=0;py<TILE_H;py++)
	{
		for (int px=0;px<TILE_W;px++)
		{
			uint8_t pix = get_pixel(x+px,y+py);
			tile->crc^=pix;
			if (clut!=NULL)
			{
				if ((pix>0xf) && (*clut==0))
				{
					*clut = pix>>4;
				}
			}
			tile->bytes[px+(py*TILE_W)] = pix&0xf;
		}
	}
}

int check_repeats(TILE *tile,bool checkflip)
{
int px,py;
	uint16_t ret=sb_count(tiles);
	tile->xflip = 0;
	for (uint16_t q=0;q<ret;q++)
	{
		int differ = 0;
		for (py=0;py<tiles[q]->height;py++)
		{
			for (px=0;px<TILE_W;px++)
			{
				if (tile->bytes[px+(py*TILE_W)]!=tiles[q]->bytes[px+(py*TILE_W)])
					differ+=1;
			}
		}


		if ((differ!=0) && (checkflip==true))
		{
			differ = 0;
			for (py=0;py<tiles[q]->height;py++)
			{
				for (px=0;px<TILE_W;px++)
				{
					if (tile->bytes[px+(py*TILE_W)]!=tiles[q]->bytes[TILE_W-1-px+(py*TILE_W)])
						differ+=1;
				}
			}
			if (differ==0)
			{
				tile->xflip = 1;
			}
		}

		if (differ==0)
			return q;

	}


	TILE *copy = dmt_malloc(sizeof(TILE));
	copy->vram_location = vram_location;
	copy->crc = tile->crc;
	copy->xflip = tile->xflip;
	copy->bytes = dmt_malloc(TILE_W*tile->height);
	copy->height = tile->height;
	memcpy(copy->bytes,tile->bytes,TILE_W*tile->height);
	sb_push(tiles,copy);

	vram_location+=tile->height/TILE_H;

	return ret;
}

void create_rrb()
{
int mw,mh,x,y,px,it,clut;
TILE tile;
uint16_t map[20];
uint16_t atr[20];
	mw = bmp_width/TILE_W;
	mh = bmp_height/TILE_H;
	tile.height = bmp_height+(TILE_H*2);
	tile.bytes = dmt_malloc(TILE_W*tile.height);
	memset(tile.bytes,0,TILE_W*tile.height);
	for (x=0;x<mw;x++)
	{
		clut = 0;
		tile.crc = 0;
		for (y=0;y<bmp_height;y++)
		{
			for (px=0;px<TILE_W;px++)
			{
				uint8_t pix = get_pixel((x*TILE_W)+px,y);
				tile.crc^=pix&0xf;
				if ((pix>0xf) && (clut==0))
				{
					clut = pix>>4;
				}
				tile.bytes[px+((y+TILE_H)*TILE_W)] = pix&0xf;
//				printf("%02X",pix&0xf);
			}
//			printf("\n");
		}
		uint16_t id = check_repeats(&tile,true);

		map[x]=tiles[id]->vram_location;
//		uint16_t ti = check_repeats(&tile) * (mh+2);
//		fwrite(&ti,sizeof(uint16_t),1,map_fp);
		atr[x] = 0x0f08;
		atr[x]|=tile.xflip<<6;
		atr[x]|=clut<<12;

//		log("rrb index t:%d x:%d c:%d",check_repeats(&tile),tile.xflip,clut);

	}

	for (y=0;y<mh+2;y++)
	{
		fwrite(&map[0],mw,sizeof(uint16_t),map_fp);		
		for (x=0;x<mw;x++)
		{
			map[x]+=1;
		}
	}
	fwrite(&atr[0],mw,sizeof(uint16_t),atr_fp);		



	dmt_free(tile.bytes);

}


//	same as RRB minus the padding

void create_sprite()
{
int mw,mh,x,y,px,it,clut;
TILE tile;
uint16_t map[20];
uint16_t atr[20];
	mw = bmp_width/TILE_W;
	mh = bmp_height/TILE_H;
	tile.height = bmp_height;
	tile.bytes = dmt_malloc(TILE_W*tile.height);
	memset(tile.bytes,0,TILE_W*tile.height);
	for (x=0;x<mw;x++)
	{
		clut = 0;
		tile.crc = 0;
		for (y=0;y<bmp_height;y++)
		{
			for (px=0;px<TILE_W;px++)
			{
				uint8_t pix = get_pixel((x*TILE_W)+px,y);
				tile.crc^=pix;
				tile.bytes[px+(y*TILE_W)] = pix&0xf;
//				printf("%02X",pix&0xf);
			}
//			printf("\n");
		}
		uint16_t id = check_repeats(&tile,false);
//		map[x]=tiles[id]->vram_location;
	}

	dmt_free(tile.bytes);

}
void create_map()
{
int mw,mh;
int y,x;
TILE_ATTRIB atr;
TILE tile;
	tile.bytes = dmt_malloc(TILE_W*TILE_H);

	mw = bmp_width/TILE_W;
	mh = bmp_height/TILE_H;

	tile_map = (TILE_ATTRIB*)dmt_malloc((mw*sizeof(TILE_ATTRIB))*mh);
	memset(tile_map,0,(mw*sizeof(TILE_ATTRIB))*mh);
	log("map is %dx%d",mw,mh);

	int it = 0;
	for (y=0;y<mh;y++)
	{
		for (x=0;x<mw;x++)
		{
			int clut;
			it = x+(y*mw);
			get_tile_4bpp(x*TILE_W,y*TILE_H,&clut,&tile);
			tile.height = TILE_H;
			tile_map[it].index=check_repeats(&tile,true);
			tile_map[it].clut = clut;
			tile_map[it].xflip = tile.xflip;
		}
	}

	for (y=0;y<mh;y++)
	{
		for (x=0;x<mw;x++)
		{
			it = x+(y*mw);
			uint16_t ti = tile_map[it].index;
			ti+=tile_offset;
			fwrite(&ti,sizeof(uint16_t),1,map_fp);
		}
	}

	for (y=0;y<mh;y++)
	{
		for (x=0;x<mw;x++)
		{
			it = x+(y*mw);
			uint16_t atr = 0x0f08;
			atr|=tile_map[it].xflip<<6;
			atr|=tile_map[it].clut<<12;
			fwrite(&atr,sizeof(uint16_t),1,atr_fp);
		}
	}
	dmt_free(tile.bytes);
	dmt_free(tile_map);
}


int main(int argc,char *argv[])
{
	int i,index;
	int nyb_swap = 0;
	tiles = NULL;
	char outname[256];
	char filename[256];
	void (*data_type)() = create_map; 
	index = 0;
	vram_location = 0;
	for(i=1;i<argc;i++)
	{
		char *isBmp=strstr(argv[i],".bmp");
		if (isBmp!=NULL)
		{
			if (bmp_load(argv[i])==1)
			{

				if (index==0)
				{
					sprintf(filename,"%s.map",outname);
					log("%s",filename);
					map_fp = fopen(filename,"wb");
					sprintf(filename,"%s.atr",outname);
					atr_fp = fopen(filename,"wb");
					//	palette is input first image					
					sprintf(filename,"%s.clut",outname);
					FILE *fp = fopen(filename,"wb");
					for (int ch=0;ch<3;ch++)
					{
						for (int q=0;q<256;q++)
						{
							uint8_t b= SWAP_UINT8(bmp_palette[q][ch]);
							fwrite(&b,1,1,fp);
						}
					}

					fclose(fp);

				}
				else 
				{
					sprintf(filename,"%s_%d.map",outname,index);
					map_fp = fopen(filename,"wb");
					sprintf(filename,"%s_%d.atr",outname,index);
					atr_fp = fopen(filename,"wb");
				}
				index+=1;

				log("bmp %s:%dx%d",argv[i],bmp_width,bmp_height);
				if (data_type!=NULL)
					data_type();

				fclose(map_fp);
				fclose(atr_fp);
			}
		}
		//	is it an option 
		if (argv[i][0]=='-')
		{
			char *o = &argv[i][1];
			if (*o=='b')
			{
				int addr = strtol(argv[i+1],NULL,16);
				tile_offset = addr/64;
				vram_location = tile_offset;

				log("address %d offset %x",addr,tile_offset);
				i+=1;
			}
			if (*o=='m')
			{
				log("map mode");
				nyb_swap = 0;
				data_type = create_map;
			}

			if (*o=='r')
			{
				log("rrb mode");
				nyb_swap = 0;
				data_type = create_rrb;
			}

			if (*o=='s')
			{
				log("sprite mode");
				nyb_swap = 1;
				data_type = create_sprite;
			}

			if (*o=='o')
			{
				log("%s",argv[i+1]);
				memset(outname,0,sizeof(outname));
				memcpy(outname,&argv[i+1][0],strlen(argv[i+1]));
				sprintf(filename,"%s.chrs",outname);
				chrs_fp = fopen(filename,"wb");
				log("%s",outname);

				i+=1;
			}
		}
		else 
		{
			log("<%s>",argv[i]);
		}
	}



	log("%d tiles",sb_count(tiles));
	for (int q=0;q<sb_count(tiles);q++)
	{
		for (int py=0;py<tiles[q]->height;py++)
		{
			for (int px=0;px<TILE_W;px+=2)
			{
				uint8_t b = tiles[q]->bytes[px+(py*TILE_W)];
				if (nyb_swap==0)
				{
					b|=tiles[q]->bytes[(1+px)+(py*TILE_W)]<<4;
				}
				else 
				{
					b = b << 4;
					b|=tiles[q]->bytes[(1+px)+(py*TILE_W)];
				}

				fwrite(&b,1,1,chrs_fp);
			}
		}
	}
	fclose(chrs_fp);

	//	free
	for (int q=0;q<sb_count(tiles);q++)
	{
		dmt_free(tiles[q]->bytes);
		dmt_free(tiles[q]);
	}
	sb_free(tiles);
	if (bmp_buffer)
		dmt_free(bmp_buffer);
	dmt_dump(stdout);

	return 0;
}


