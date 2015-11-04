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

%feature("docstring") praxyk::get_strings_from_images \
"
Parses the given images for strings in parallel.

Args:
    filenames (praxyk.string_vector): List of filepaths to the images to scan.
    max_at_once (int): Optional argument. Throttles the number of images scanned in parallel.

Returns:
    praxyk.string_vector: List of strings found in images. An entry is empty if
                          no string is found in the given image.

Raises:
    RuntimeError: If the Tesseract OCR library fails to initialize.
                  If a given filename does not exist.
                  If a given image is invalid.
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
