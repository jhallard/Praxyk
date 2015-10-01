INCLUDE_DIRECTORIES(
    ${CMAKE_SOURCE_DIR}/include
)

SET(praxyk_utils
    praxyk-util1
    praxyk-util2
)

FOREACH(util ${praxyk_utils})
    ADD_EXECUTABLE(${util} ${util}.cpp)
    TARGET_LINK_LIBRARIES(${util} praxyk)
    INSTALL(
        TARGETS ${util}
        DESTINATION ${RUNTIME_DIR}
        COMPONENT Utilities
    )
ENDFOREACH(util ${praxyk_utils})

INSTALL(
    PROGRAMS praxyk-python-util.py
    DESTINATION ${RUNTIME_DIR}
    COMPONENT Utilities
)
