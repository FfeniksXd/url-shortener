#include <stdlib.h>
#include <string.h>

extern "C" {
    char* get_test() {
        char* res = (char*)malloc(20);
        if (res) strcpy(res, "test|test|test");
        return res;
    }
    void free_string(char* s) { free(s); }
}