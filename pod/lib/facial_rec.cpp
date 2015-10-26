#include <praxyk/facial_rec.hpp>
#include <praxyk/paths.hpp>

#include "clandmark/CSparseLBPFeatures.h"
#include "clandmark/Flandmark.h"

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/objdetect/objdetect.hpp>

#include <stdexcept>
#include <vector>

namespace praxyk {
    face_boxes_t detect_faces_in_image(
        const std::string &filename
    ) {
        const std::string flandmark_model = get_clandmark_dir() + "/flandmark_model.xml";
        const std::string cascade_name = get_clandmark_dir() + "/haarcascade_frontalface_alt.xml";

        face_boxes_t ret;

        /*
         * Initialization
         */
        clandmark::Flandmark* flandmark = clandmark::Flandmark::getInstanceOf(
                                               flandmark_model.c_str(), false
                                          );
        if(!flandmark) {
            throw std::runtime_error("Failed to initialize CLandmark.");
        }

        clandmark::CFeaturePool* featurePool = new clandmark::CFeaturePool(
                                                       flandmark->getBaseWindowSize()[0],
                                                       flandmark->getBaseWindowSize()[1]
                                                   );
        featurePool->addFeaturesToPool(
                         new clandmark::CSparseLBPFeatures(
                                 featurePool->getWidth(),
                                 featurePool->getHeight(),
                                 featurePool->getPyramidLevels(),
                                 featurePool->getCumulativeWidths()
                             )
                     );
        flandmark->setNFfeaturesPool(featurePool);

        cv::CascadeClassifier face_cascade;
        if(!face_cascade.load(cascade_name)) {
            throw std::runtime_error("Failed to initialize Face Cascade.");
        }

        cv::Mat image = cv::imread(filename);
        if(image.empty()) {
            throw std::runtime_error("Failed to open image.");
        }

        /*
         * Actual face detection
         */
        std::vector<cv::Rect> faces;
        int bbox[8];

        cv::Mat image_gray;
        cv::cvtColor(image, image_gray, CV_BGR2GRAY);
        face_cascade.detectMultiScale(
            image_gray, faces,
            1.1, 2, (0 | CV_HAAR_SCALE_IMAGE),
            cv::Size(30, 30)
        );

        /*
         * Cleanup
         */
        delete featurePool;
        delete flandmark;

        return ret;
    }
}
