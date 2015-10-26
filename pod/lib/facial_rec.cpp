#include <praxyk/facial_rec.hpp>

#include "clandmark/Flandmark.h"

namespace praxyk {
    face_boxes_t detect_faces_in_image(
        const std::string &filename
    ) {
        face_boxes_t ret;

        clandmark::Flandmark* flandmark = clandmark::Flandmark::getInstanceOf(
                                               filename.c_str(), false
                                          );

        return ret;
    }
}
