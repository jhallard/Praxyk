CONFIGURE_FILE(
    ${CMAKE_CURRENT_SOURCE_DIR}/paths.cpp.in
    ${CMAKE_CURRENT_BINARY_DIR}/paths.cpp
@ONLY)

SET(praxyk_sources
    facial_rec.cpp
    ocr.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/paths.cpp
    spam.cpp
)

INCLUDE_DIRECTORIES(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CLANDMARK_INCLUDE_DIRS}
    ${FANN_INCLUDE_DIRS}
    ${Tesseract_INCLUDE_DIR}
    ${Mlpack_INCLUDE_DIR}
    ${LIBXML2_INCLUDE_DIR}
    ${OpenCV_INCLUDE_DIR}
)

SET(praxyk_libs
    ${CLANDMARK_LIBRARIES}
    ${FANN_LIBRARIES}
    ${Tesseract_LIBRARIES}
    ${Boost_LIBRARIES}
    ${Mlpack_LIBRARIES}
    ${LIBXML2_LIBRARIES}
    ${OpenCV_LIBRARIES}
    clandmark
)

ADD_DEFINITIONS(-DPRAXYK_DLL_EXPORTS)
ADD_LIBRARY(praxyk SHARED ${praxyk_sources})
TARGET_LINK_LIBRARIES(praxyk ${praxyk_libs})

INSTALL(
    TARGETS praxyk
    LIBRARY DESTINATION ${LIBRARY_DIR} COMPONENT Libraries
)
