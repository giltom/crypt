#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BIT_IS_SET(BMP, I) ((BMP)[(I)/8] & (1 << ((I)%8)))
#define UNSET_BIT(BMP, I) (BMP)[(I)/8] &= ~(1 << ((I)%8))

//integer square root (rounded down)
unsigned long isqrt(unsigned long n){
	unsigned long x = n;
    unsigned long y = (x + 1) / 2;
    while (y < x) {
        x = y;
        y = (x + n / x) / 2;
	}
    return x;
}

void write_bin_num(FILE* fp, unsigned long n){
	while (n){
		fputc(n & 0xFF, fp);
		n >>= 8;
	}
	fputc(0, fp);
}

int main(int argc, char* argv[]){
	if (argc != 4){
		printf("Usage: %s <max-number> <output-filename> {t,b}\n", argv[0]);
		return 1;
	}

	unsigned long n;
	sscanf(argv[1], "%lu", &n);
	unsigned long sqrtn = isqrt(n);
	unsigned long bmplen = n / 8 + 1;
	char* bmp = (char*) malloc(bmplen);
	memset(bmp, 0xFF, bmplen);

	for (unsigned long i = 2; i <= sqrtn; i++)
		if (BIT_IS_SET(bmp, i))
			for (unsigned long j = i*i; j <= n; j += i)
				UNSET_BIT(bmp, j);

	FILE* fp;
	if (argv[3][0] == 't')
		fp = fopen(argv[2], "w");
	else
		fp = fopen(argv[2], "wb");
	for (unsigned long i = 2; i <= n; i++)
		if (BIT_IS_SET(bmp, i)){
			if (argv[3][0] == 't')
				fprintf(fp, "%lX\n", i);
			else
				write_bin_num(fp, i);
		}

	fclose(fp);
	free(bmp);
	return 0;
}
