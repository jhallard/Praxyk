%{
    #include <praxyk/facial_rec.hpp>
    #include <praxyk/ocr.hpp>
    #include <praxyk/paths.hpp>
    #include <praxyk/spam.hpp>

    #include <stdexcept>
%}

// Catch C++ exceptions and turn them into Python RuntimeErrors so
// we don't segfault.
%exception {
    try {
        $action
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, const_cast<char*>(e.what()));
        return NULL;
    } catch (...) {
        PyErr_SetString(PyExc_RuntimeError, "Caught unknown error");
        return NULL;
    }
}

%include <std_map.i>
%include <std_string.i>
%include <std_vector.i>
%template(string_vector) std::vector<std::string>;

%include <praxyk_docstrings.i>
%include <praxyk/config.hpp>

%include <praxyk/facial_rec.hpp>
%template(face_map)  std::map<std::string, praxyk::coords_t>;
%template(face_maps) std::vector<std::map<std::string, praxyk::coords_t> >;

%include <praxyk/ocr.hpp>
%include <praxyk/paths.hpp>
%include <praxyk/spam.hpp>

