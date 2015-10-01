SET(praxyk_headers
    config.hpp
    src1.hpp
    src2.hpp
)

INSTALL(
    FILES ${praxyk_headers}
    DESTINATION ${INCLUDE_DIR}/praxyk
)
