#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>

// Typedef for the function signature: int, int -> int
typedef int (*op_func)(int, int);

int main() {
    char op[10];
    int num1, num2;
    char lib_name[30];
    
    // Read inputs in a loop until EOF
    while (scanf("%s %d %d", op, &num1, &num2) == 3) {
        // Construct library name, e.g., "./libadd.so"
        snprintf(lib_name, sizeof(lib_name), "./lib%s.so", op);
        
        // Load the shared library at runtime
        void *handle = dlopen(lib_name, RTLD_LAZY);
        if (!handle) {
            fprintf(stderr, "Error loading library %s: %s\n", lib_name, dlerror());
            continue;
        }
        
        // Clear any existing error
        dlerror();
        
        // Get the address of the function with the name <op>
        op_func func = (op_func)dlsym(handle, op);
        char *error = dlerror();
        if (error != NULL) {
            fprintf(stderr, "Error finding symbol %s: %s\n", op, error);
            dlclose(handle);
            continue;
        }
        
        // Call the function and print the result
        int result = func(num1, num2);
        printf("%d\n", result);
        
        // Unload the library to respect the 2GB memory constraint.
        // Since each library can be up to 1.5GB, keeping more than one
        // loaded could exceed the limit.
        dlclose(handle);
    }
    
    return 0;
}
