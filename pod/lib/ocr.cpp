#include <praxyk/ocr.hpp>

#include <boost/thread/thread.hpp>

#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>

#include <algorithm>
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

std::vector<std::string> get_strings_from_images(
    const std::vector<std::string> &filenames,
    const size_t max_at_once
) {
    std::vector<std::string> ret(filenames.size());

    size_t current_index = 0;
    while(current_index < filenames.size()) {
        size_t num_to_process = 0;
        if(max_at_once == 0) {
            num_to_process = filenames.size();
        } else {
            num_to_process = std::min<size_t>(
                                 max_at_once,
                                 (filenames.size() - current_index)
                             );
        }

        boost::thread_group thread_group;
        for(size_t i = current_index;
            i < (current_index+num_to_process);
            i++) {

            thread_group.create_thread(
                boost::bind(&_get_string_from_image,
                            filenames[i], &ret[i]
                           )
            );
        }
        thread_group.join_all();
        current_index += num_to_process;
    }

    return ret;
}

}
