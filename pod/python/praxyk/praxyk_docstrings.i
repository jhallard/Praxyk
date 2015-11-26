%feature("autodoc", "0");

%feature("docstring") praxyk::get_string_from_image \
"
Parses the given image for strings.

Args:
    filename (str): Filepath to the image to scan

Returns:
    str: String found in image. Empty if no string found.

Raises:
    RuntimeError: If the Tesseract OCR library fails to initialize.
                  If the given filename does not exist.
                  If the given image is invalid.
                  Any other C++ exception.
"

%feature("docstring") praxyk::get_pkg_data_dir \
"
Returns the directory where Praxyk's data (trained data, etc). The function starts by checking
the environment variable PRAXYK_PKG_DATA_DIR. If this environment variable is not set, it defaults
to where CMake installed Praxyk. By default, this directory is \"(INSTALL PREFIX)/share/praxyk\".

Returns:
    str: Praxyk's data directory
"

%feature("docstring") praxyk::get_clandmark_dir \
"
Returns the directory where Praxyk stores the trained data used internally by CLandmark for facial
feature recognition.
"

%feature("docstring") praxyk::get_mlpack_dir \
"
Returns the directory where Praxyk stores the trained data used internally by MLPack for spam detection.
"
