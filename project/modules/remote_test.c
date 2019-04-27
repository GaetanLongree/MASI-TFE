#include <stdio.h>

#define LEN 256

int main (int argc, char **argv)
{
    char *input = argv[1];
    FILE * fp;
    // open the file for writing
    fp = fopen("c_module_output.txt","w");
    fprintf(fp, "%s", input);
    // close the file
    fclose (fp);

    // return the user input for next modules
    printf("%s", input);
    return 0;
}