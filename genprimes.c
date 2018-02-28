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

int main(int argc, char* argv[]){
	if (argc != 3){
		printf("Usage: %s <max-number> <output-filename>\n", argv[0]);
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

	FILE* fp = fopen(argv[2], "w");;
	for (unsigned long i = 2; i <= n; i++)
		if (BIT_IS_SET(bmp, i))
			fprintf(fp, "%lX\n", i);

	fclose(fp);
	free(bmp);
	return 0;
}
