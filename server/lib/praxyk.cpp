#include <praxyk/praxyk.hpp>

#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>

#include <stdexcept>

namespace praxyk {

std::string get_string_from_image(
    const std::string &filename
) {
    std::string outText;

    tesseract::TessBaseAPI *api = new tesseract::TessBaseAPI();
    // Initialize tesseract-ocr with English, without specifying tessdata path
    if (api->Init(NULL, "eng")) {
        throw std::runtime_error("Failed to initialize Tesseract.");
    }

    // Open input image with leptonica library
    Pix *image = pixRead(filename.c_str());
    api->SetImage(image);
    // Get OCR result
    outText = api->GetUTF8Text();

    // Destroy used object and release memory
    api->End();
    pixDestroy(&image);

    return outText;
}

}
