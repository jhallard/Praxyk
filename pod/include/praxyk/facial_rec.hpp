#ifndef INCLUDED_PRAXYK_FACIAL_REC_HPP
#define INCLUDED_PRAXYK_FACIAL_REC_HPP

#include <praxyk/config.hpp>

#include <map>
#include <string>
#include <vector>

namespace praxyk {

typedef struct {
    size_t x;
    size_t y;
} coords_t;

typedef std::map<std::string, coords_t> face_map_t;
typedef std::vector<face_map_t> face_maps_t;

PRAXYK_API face_maps_t detect_faces_in_image(
    const std::string &filename
);

}

#endif /* INCLUDED_PRAXYK_FACIAL_REC_HPP */
