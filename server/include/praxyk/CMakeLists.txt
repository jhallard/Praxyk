SET(praxyk_headers
    config.hpp
    praxyk.hpp
    src2.hpp
)

INSTALL(
    FILES ${praxyk_headers}
    DESTINATION ${INCLUDE_DIR}/praxyk
)
