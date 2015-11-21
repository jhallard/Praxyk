#include <praxyk/ocr.hpp>
#include <praxyk/paths.hpp>

#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>

#include <algorithm>
#include <cstdlib>
#include <stdexcept>

namespace praxyk {

std::string get_string_from_image(
    const std::string &filename
) {
    // Tell Tesseract to look at our trained data
    const std::string tessdata_prefix = get_pkg_data_dir();
    if(setenv("TESSDATA_PREFIX", tessdata_prefix.c_str(), 1)) {
        throw std::runtime_error("Failed to set TESSDATA_PREFIX environment variable.");
    }

    // Create Tesseract instance
    tesseract::TessBaseAPI *api = new tesseract::TessBaseAPI();
    if (api->Init(NULL, "eng")) {
        throw std::runtime_error("Failed to initialize Tesseract.");
    }

    // Read image
    Pix *image = pixRead(filename.c_str());
    if(!image){
        throw std::runtime_error("Error reading image");
    }

    // Open input image with leptonica library
    api->SetImage(image);
    // Get OCR result
    std::string ret = api->GetUTF8Text();

    // Destroy used object and release memory
    api->End();
    pixDestroy(&image);

    // Remove duplicate newlines from end of string
    while(ret[ret.length()-1] == '\n') {
        ret.pop_back();
    }
    return ret;
}

}
