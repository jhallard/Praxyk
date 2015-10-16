SET(praxyk_sources
    ocr.cpp
    spam.cpp
)

INCLUDE_DIRECTORIES(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${FANN_INCLUDE_DIRS}
    ${Tesseract_INCLUDE_DIR}
    ${Mlpack_INCLUDE_DIR}
    ${LIBXML2_INCLUDE_DIR}
)

SET(praxyk_libs
    ${FANN_LIBRARIES}
    ${Tesseract_LIBRARIES}
    ${Boost_LIBRARIES}
    ${Mlpack_LIBRARIES}
    ${LIBXML2_LIBRARIES}
)

ADD_DEFINITIONS(-DPRAXYK_DLL_EXPORTS)
ADD_LIBRARY(praxyk SHARED ${praxyk_sources})
TARGET_LINK_LIBRARIES(praxyk ${praxyk_libs})

INSTALL(
    TARGETS praxyk
    LIBRARY DESTINATION ${LIBRARY_DIR} COMPONENT Libraries
)
