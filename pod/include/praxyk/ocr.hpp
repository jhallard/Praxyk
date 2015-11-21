#ifndef INCLUDED_PRAXYK_OCR_HPP
#define INCLUDED_PRAXYK_OCR_HPP

#include <praxyk/config.hpp>

#include <string>
#include <vector>

namespace praxyk {

PRAXYK_API std::string get_string_from_image(
    const std::string &filename
);

}

#endif /* INCLUDED_PRAXYK_OCR_HPP */
