%{
    #include <praxyk/ocr.hpp>
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

%include <std_string.i>
%include <std_vector.i>
%template(string_vector) std::vector<std::string>;

%include <praxyk/config.hpp>
%include <praxyk/ocr.hpp>
%include <praxyk/spam.hpp>
