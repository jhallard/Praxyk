#include <praxyk/ocr.hpp>

#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>

#include <stdexcept>

namespace praxyk {

void _get_string_from_image(
    const std::string &filename,
    std::string *ret
) {
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
    *ret = api->GetUTF8Text();

    // Destroy used object and release memory
    api->End();
    pixDestroy(&image);

    // Remove duplicate newlines from end of string
    while((*ret)[ret->length()-1] == '\n') {
        ret->pop_back();
    }
}

std::string get_string_from_image(
    const std::string &filename
) {
    std::string ret;
    _get_string_from_image(filename, &ret);
    return ret;
}

}
