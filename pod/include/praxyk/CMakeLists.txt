SET(praxyk_headers
    config.hpp
    facial_rec.hpp
    paths.hpp
    ocr.hpp
    spam.hpp
)

INSTALL(
    FILES ${praxyk_headers}
    DESTINATION ${INCLUDE_DIR}/praxyk
)
