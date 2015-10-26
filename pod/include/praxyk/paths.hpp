#ifndef INCLUDED_PRAXYK_PATHS_HPP
#define INCLUDED_PRAXYK_PATHS_HPP

#include <praxyk/config.hpp>

#include <string>

namespace praxyk {
    PRAXYK_API std::string get_pkg_data_dir();

    PRAXYK_INLINE std::string get_landmark_dir() {
        return (get_pkg_data_dir() + "/landmark");
    }
}

#endif /* INCLUDED_PRAXYK_PATHS_HPP */
