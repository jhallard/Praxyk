INCLUDE_DIRECTORIES(
    ${CMAKE_CURRENT_SOURCE_DIR}
)

SET(NEURAL2D_SOURCES
    imageReaderBMP.cpp
    imageReaderDat.cpp
    neural2d-core.cpp
    parseTopologyConfig.cpp
)

# TODO: make sure -std=c++11 works with Clang
ADD_DEFINITIONS("-Wall -Wextra -Wpedantic -std=c++11 -DDISABLE_WEBSERVER")
ADD_LIBRARY(neural2d STATIC ${NEURAL2D_SOURCES})
