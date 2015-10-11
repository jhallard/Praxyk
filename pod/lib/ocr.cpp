#include <praxyk/ocr.hpp>

#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>

#include <stdexcept>

namespace praxyk {

std::string get_string_from_image(
    const std::string &filename
) {
    std::string outText;

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
    outText = api->GetUTF8Text();

    // Destroy used object and release memory
    api->End();
    pixDestroy(&image);

    // Remove duplicate newlines from end of string
    while(outText[outText.length()-1] == '\n') {
        outText.pop_back();
    }

    return outText;
}

}
