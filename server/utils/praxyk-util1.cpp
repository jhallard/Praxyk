#include <praxyk/src1.hpp>

#include <cstdlib>
#include <iostream>

int main() {
    int praxyk_int = praxyk::return_int();
    std::string praxyk_string = praxyk::return_string();

    std::cout << "praxyk_int = " << praxyk_int << std::endl;
    std::cout << "praxyk_string = " << praxyk_string << std::endl;

    return EXIT_SUCCESS;
}
