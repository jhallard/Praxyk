#include <praxyk/praxyk.hpp>

#include <cstdlib>
#include <iostream>

int main(int argc, char* argv[]) {
    std::cout << "string from image: " << praxyk::get_string_from_image(argv[1]) << std::endl;

    return EXIT_SUCCESS;
}
