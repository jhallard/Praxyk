#include <praxyk/config.hpp>

#include <string>
#include <vector>

namespace praxyk {

PRAXYK_API std::string get_string_from_image(
    const std::string &filename
);

PRAXYK_API std::vector<std::string> get_strings_from_images(
    const std::vector<std::string> &filenames
);

}
