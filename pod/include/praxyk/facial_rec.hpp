#ifndef INCLUDED_PRAXYK_FACIAL_REC_HPP
#define INCLUDED_PRAXYK_FACIAL_REC_HPP

#include <praxyk/config.hpp>

#include <string>
#include <vector>

namespace praxyk {

typedef struct {
    int x;
    int y;
} coords_t;

typedef struct {
    coords_t head;
    coords_t left_eye;
    coords_t right_eye;
} face_coords_t;

typedef std::vector<face_coords_t> face_coords_vector_t;

PRAXYK_API std::vector<face_coords_t> detect_faces_in_image(
    const std::string &filename
);

}

/* INCLUDED_PRAXYK_FACIAL_REC_HPP */
