#include <praxyk/src2.hpp>

#include <cstdlib>
#include <iostream>

int main() {
    double praxyk_double = praxyk::return_double();
    char praxyk_char = praxyk::return_char();

    std::cout << "praxyk_double = " << praxyk_double << std::endl;
    std::cout << "praxyk_char = " << praxyk_char << std::endl;

    return EXIT_SUCCESS;
}
