#ifndef INCLUDED_PRAXYK_FACIAL_REC_HPP
#define INCLUDED_PRAXYK_FACIAL_REC_HPP

#include <praxyk/config.hpp>

#include <string>
#include <vector>

namespace praxyk {

typedef struct {
    int x;
    int y;

    int width;
    int height;
} box_t;

typedef struct {
    box_t head;
    box_t left_eye;
    box_t right_eye;
    box_t mouth;
} face_box_t;

typedef std::vector<face_box_t> face_boxes_t;

PRAXYK_API face_boxes_t detect_faces_in_image(
    const std::string &filename
);

}

#endif /* INCLUDED_PRAXYK_FACIAL_REC_HPP */
