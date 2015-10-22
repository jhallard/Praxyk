SET(praxyk_headers
    config.hpp
    paths.hpp
    ocr.hpp
    spam.hpp
)

INSTALL(
    FILES ${praxyk_headers}
    DESTINATION ${INCLUDE_DIR}/praxyk
)
