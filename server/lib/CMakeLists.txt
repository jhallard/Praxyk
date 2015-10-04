SET(praxyk_sources
    praxyk.cpp
    src2.cpp
)

INCLUDE_DIRECTORIES(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${Tesseract_INCLUDE_DIR}
)

ADD_DEFINITIONS(-DPRAXYK_DLL_EXPORTS)
ADD_LIBRARY(praxyk SHARED ${praxyk_sources} ${Tesseract_LIBRARIES})

INSTALL(
    TARGETS praxyk
    LIBRARY DESTINATION ${LIBRARY_DIR} COMPONENT Libraries
)
