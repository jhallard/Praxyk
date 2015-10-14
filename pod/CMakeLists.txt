########################################################################
# CMake configuration
########################################################################
CMAKE_MINIMUM_REQUIRED(VERSION 2.6)
PROJECT(praxyk C CXX)
ENABLE_TESTING()

SET(praxyk_VERSION_MAJOR 0)
SET(praxyk_VERSION_MINOR 0)
SET(praxyk_VERSION_PATCH 1)

SET(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/Modules;${CMAKE_MODULE_PATH}")

########################################################################
# Search for dependencies here
########################################################################
FIND_PACKAGE(FANN REQUIRED)
FIND_PACKAGE(Tesseract REQUIRED)

SET(BOOST_REQUIRED_COMPONENTS
    thread
)
FIND_PACKAGE(Boost 1.48 COMPONENTS ${BOOST_REQUIRED_COMPONENTS})
IF(NOT ${Boost_FOUND})
    MESSAGE(FATAL_ERROR "Boost.Thread is required.")
ENDIF(NOT ${Boost_FOUND})

########################################################################
# Global flags
########################################################################
IF(CMAKE_COMPILER_IS_GNUCXX OR "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -fvisibility=hidden")
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -fvisibility=hidden -std=c++11")
ENDIF(CMAKE_COMPILER_IS_GNUCXX OR "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")

########################################################################
# Create uninstall target
########################################################################
CONFIGURE_FILE(
    ${CMAKE_SOURCE_DIR}/cmake/cmake_uninstall.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake
@ONLY)

ADD_CUSTOM_TARGET(uninstall
    ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake
)

####################################################################
# Set install subdirectories
####################################################################
IF(NOT DEFINED LIB_SUFFIX AND REDHAT AND CMAKE_SYSTEM_PROCESSOR MATCHES "64$")
    SET(LIB_SUFFIX 64)
ENDIF()
SET(LIB_SUFFIX ${LIB_SUFFIX} CACHE STRING "lib directory suffix")
SET(RUNTIME_DIR bin)
SET(LIBRARY_DIR lib${LIB_SUFFIX})
SET(INCLUDE_DIR include)
SET(PKG_DATA_DIR share/praxyk)
SET(DOCS_DIR share/doc/praxyk)

ADD_SUBDIRECTORY(include)
ADD_SUBDIRECTORY(lib)
ADD_SUBDIRECTORY(python)
ADD_SUBDIRECTORY(tests)

####################################################################
# Final Display
####################################################################
MESSAGE(STATUS "")
MESSAGE(STATUS "Building Praxyk - Server Side.")
MESSAGE(STATUS " - Build type: ${CMAKE_BUILD_TYPE}")
MESSAGE(STATUS " - Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
MESSAGE(STATUS "")
