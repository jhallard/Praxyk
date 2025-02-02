# - Try to find the clandmark landmark detector library
#
# =============================================================================
# Once done this will define:
#
#  CLANDMARK_FOUND          TRUE if found; FALSE otherwise
#  CLANDMARK_INCLUDE_DIRS   where to find flandmark_detector.h
#  CLANDMARK_LIBRARIES      the libraries to link against
#
# =============================================================================
# Variables used by this module:
#
#  CLANDMARK_PREFER_STATIC  If TRUE and available, link against the static
#                           flandmark library. Otherwise select the shared
#                           version
#
# =============================================================================
# To use this from another project:
#
# create a directory named cmake/Modules under the project root, copy this file
# (FindCLANDMARK.cmake) there, and in the top-level CMakeLists.txt include:
#   set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
#                         "${CMAKE_SOURCE_DIR}/cmake/Modules/")
#
# =============================================================================

find_path(CLANDMARK_INCLUDE_DIR clandmark/CLandmark.h)
find_library(CLANDMARK_LIBRARY NAMES clandmark)

set(CLANDMARK_LIBRARIES ${CLANDMARK_LIBRARY})
set(CLANDMARK_INCLUDE_DIRS ${CLANDMARK_INCLUDE_DIR})

include(FindPackageHandleStandardArgs)
# handle the QUIETLY and REQUIRED arguments and set CLANDMARK_FOUND to TRUE
# if all listed variables are TRUE
find_package_handle_standard_args(
	CLANDMARK
	DEFAULT_MSG
	CLANDMARK_LIBRARY CLANDMARK_INCLUDE_DIR
)

mark_as_advanced(CLANDMARK_INCLUDE_DIR CLANDMARK_LIBRARY)
