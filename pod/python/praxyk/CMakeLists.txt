FIND_PACKAGE(PythonInterp 2)
FIND_PACKAGE(PythonLibs 2)
FIND_PACKAGE(SWIG)

IF(SWIG_FOUND AND PYTHONLIBS_FOUND AND PYTHONINTERP_FOUND)
    INCLUDE(UseSWIG)
    SET(CMAKE_SWIG_FLAGS -module praxyk_python)
    SET_SOURCE_FILES_PROPERTIES(praxyk_python.i PROPERTIES CPLUSPLUS ON)
    SET(PRAXYK_PYTHON_INCLUDE_DIRS
        ${CMAKE_SOURCE_DIR}/include
        ${PYTHON_INCLUDE_DIR}
    )
    INCLUDE_DIRECTORIES(${PRAXYK_PYTHON_INCLUDE_DIRS})
    FOREACH(dir ${PRAXYK_PYTHON_INCLUDE_DIRS})
        LIST(APPEND CMAKE_SWIG_FLAGS "-I${dir}")
    ENDFOREACH(dir ${PRAXYK_PYTHON_INCLUDE_DIRS})

    SWIG_ADD_MODULE(praxyk_python python praxyk_python.i)
    SWIG_LINK_LIBRARIES(praxyk_python praxyk ${PYTHON_LIBRARIES})

    #
    # Set the Python install directory
    #
    EXECUTE_PROCESS(COMMAND ${PYTHON_EXECUTABLE} -c "
from distutils import sysconfig
print(sysconfig.get_python_lib(plat_specific=True, prefix=''))
    " OUTPUT_VARIABLE PRAXYK_PYTHON_DIR OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    FILE(TO_CMAKE_PATH ${PRAXYK_PYTHON_DIR} PRAXYK_PYTHON_DIR)
    SET(PRAXYK_PYTHON_DIR ${PRAXYK_PYTHON_DIR} CACHE FILEPATH "Python install directory")

    SET(PRAXYK_PYTHON_FILES
        __init__.py
        facial_tools.py
        spam.py
    )

    FOREACH(pyfile ${PRAXYK_PYTHON_FILES})
        CONFIGURE_FILE(
            ${CMAKE_CURRENT_SOURCE_DIR}/${pyfile}
            ${CMAKE_CURRENT_BINARY_DIR}/${pyfile}
        )
    ENDFOREACH(pyfile ${PRAXYK_PYTHON_FILES})

    LIST(APPEND PRAXYK_PYTHON_FILES
        ${CMAKE_CURRENT_BINARY_DIR}/praxyk_python.py
    )

    INSTALL(
        FILES ${PRAXYK_PYTHON_FILES}
        DESTINATION ${PRAXYK_PYTHON_DIR}/praxyk
        COMPONENT Python
    )
    INSTALL(
        TARGETS ${SWIG_MODULE_praxyk_python_REAL_NAME}
        DESTINATION ${PRAXYK_PYTHON_DIR}/praxyk
        COMPONENT Python
    )
ENDIF(SWIG_FOUND AND PYTHONLIBS_FOUND AND PYTHONINTERP_FOUND)
