#include <cstdlib>
#include <cstring>
#include <random>

// Глобальные генераторы случайных чисел (инициализируются один раз)
static std::mt19937 gen(std::random_device{}());
static std::uniform_int_distribution<> dis(0, 61); // 62 символа

extern "C" {
    char* generate_code(int length) {
        static const char alphanum[] = 
            "0123456789"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz";

        char* result = (char*)malloc(length + 1);
        if (result == nullptr) return nullptr;

        for (int i = 0; i < length; ++i) {
            result[i] = alphanum[dis(gen)];
        }
        result[length] = '\0';
        return result;
    }

    void free_string(char* str) {
        if (str != nullptr) free(str);
    }
}