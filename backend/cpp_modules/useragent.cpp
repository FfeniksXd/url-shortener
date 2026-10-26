#include <string.h>
#include <stdlib.h>
#include <stdio.h>

extern "C" {
    char* parse_user_agent(const char* ua) {
        if (!ua) {
            // Выделяем достаточно места для "unknown|unknown|unknown" (23 символа + 1)
            char* res = (char*)malloc(24);
            if (res) strcpy(res, "unknown|unknown|unknown");
            return res;
        }
        
        const char* device = "desktop";
        const char* os = "unknown";
        const char* browser = "unknown";
        
        if (strstr(ua, "Mobile") || (strstr(ua, "Android") && strstr(ua, "Mobile")) || strstr(ua, "iPhone") || strstr(ua, "iPad")) {
            device = "mobile";
        }
        
        if (strstr(ua, "Windows")) os = "Windows";
        else if (strstr(ua, "Macintosh")) os = "macOS";
        else if (strstr(ua, "Linux")) os = "Linux";
        else if (strstr(ua, "Android")) os = "Android";
        else if (strstr(ua, "iPhone") || strstr(ua, "iPad")) os = "iOS";
        
        if (strstr(ua, "Edg")) browser = "Edge";
        else if (strstr(ua, "Firefox")) browser = "Firefox";
        else if (strstr(ua, "Safari")) {
            if (strstr(ua, "Chrome")) browser = "Chrome";
            else browser = "Safari";
        }
        else if (strstr(ua, "Chrome")) browser = "Chrome";
        else if (strstr(ua, "Opera") || strstr(ua, "OPR")) browser = "Opera";
        
        size_t len = strlen(device) + 1 + strlen(os) + 1 + strlen(browser) + 1;
        char* result = (char*)malloc(len);
        if (result) {
            snprintf(result, len, "%s|%s|%s", device, os, browser);
        }
        return result;
    }
    
    void free_string(char* str) {
        if (str) free(str);
    }
}