#ifndef INCLUDED_PRAXYK_OCR_HPP
#define INCLUDED_PRAXYK_OCR_HPP

#include <praxyk/config.hpp>

#include <string>
#include <vector>

namespace praxyk {

PRAXYK_API std::string get_string_from_image(
    const std::string &filename
);

PRAXYK_API std::vector<std::string> get_strings_from_images(
    const std::vector<std::string> &filenames,
    const size_t max_at_once = 0
);

}

/* INCLUDED_PRAXYK_OCR_HPP */
