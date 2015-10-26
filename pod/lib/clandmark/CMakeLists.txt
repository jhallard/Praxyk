CONFIGURE_FILE(
    ${CMAKE_CURRENT_SOURCE_DIR}/CLandmarkConfig.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/CLandmarkConfig.h
)

INCLUDE_DIRECTORIES(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${OpenCV_INCLUDE_DIRS}
)

SET(clandmark_libs
    ${OpenCV_LIBRARIES}
    gomp
)

FIND_PACKAGE(OpenMP)
IF(OPENMP_FOUND)
    SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    LIST(APPEND clandmark_libs gomp)
ELSE(OPENMP_FOUND)
    SET(USE_OPENMP OFF)
ENDIF(OPENMP_FOUND)

ADD_DEFINITIONS(-fPIC)

SET(clandmark_srcs
    CLandmark.cpp
    CFeaturePool.cpp
    CFeatures.cpp
    CAppearanceModel.cpp
    CDeformationCost.cpp
    CLoss.cpp
    CMaxSumSolver.cpp
    CXMLInOut.cpp
)

ADD_LIBRARY(clandmark STATIC ${clandmark_srcs})
TARGET_LINK_LIBRARIES(clandmark ${clandmark_libs})
SET_TARGET_PROPERTIES(clandmark PROPERTIES POSITION_INDEPENDENT_CODE TRUE)	# -fPIC


SET(flandmark_srcs
    Flandmark.cpp
    CSparseLBPFeatures.cpp
    CSparseLBPAppearanceModel.cpp
    CDisplacementDeformationCost.cpp
    CNormalizedEuclideanLoss.cpp
    CTableLoss.cpp
    CZeroLoss.cpp
    CTreeMaxSumSolver.cpp
)

ADD_LIBRARY(flandmark STATIC ${flandmark_srcs})
TARGET_LINK_LIBRARIES(flandmark clandmark)
SET_TARGET_PROPERTIES(clandmark PROPERTIES POSITION_INDEPENDENT_CODE TRUE)	# -fPIC

SET(landmark_data
    data/8Lfrontal_SPLIT_1_init.xml
    data/flandmark_model.xml
    data/haarcascade_frontalface_alt.xml
)
INSTALL(
    FILES ${landmark_data}
    DESTINATION ${PKG_DATA_DIR}/landmark
    COMPONENT "Data"
)
