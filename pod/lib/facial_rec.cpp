#include <praxyk/facial_rec.hpp>
#include <praxyk/paths.hpp>

#include "clandmark/CSparseLBPFeatures.h"
#include "clandmark/Flandmark.h"

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/objdetect/objdetect.hpp>

#include <sstream>
#include <stdexcept>
#include <vector>

namespace praxyk {
    static cimg_library::CImg<unsigned char>* cvImg_to_CImg(
        const cv::Mat &cvImg
    ) {
        cimg_library::CImg<unsigned char>* result = new cimg_library::CImg<unsigned char>(
                                                            cvImg.cols, cvImg.rows
                                                        );
        for(int i = 0; i < cvImg.cols; ++i) {
            for(int j = 0; j < cvImg.rows; ++j) {
                (*result)(i,j) = cvImg.at<uchar>(j,i);
            }
        }

        return result;
    }

    face_maps_t detect_faces_in_image(
        const std::string &filename
    ) {
        const std::string flandmark_model = get_clandmark_dir() + "/flandmark_model.xml";
        const std::string cascade_name = get_clandmark_dir() + "/haarcascade_frontalface_alt.xml";

        /*
         * Initialization
         */
        face_maps_t ret;
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
        for(size_t i = 0; i < faces.size(); i++) {
            // Bounding box for finding facial features
            bbox[0] = faces[i].x;
            bbox[1] = faces[i].y;
            bbox[2] = faces[i].x+faces[i].width;
            bbox[3] = faces[i].y;
            bbox[4] = faces[i].x+faces[i].width;
            bbox[5] = faces[i].y+faces[i].height;
            bbox[6] = faces[i].x;
            bbox[7] = faces[i].y+faces[i].height;

            // Face location and dimensions
            face_map_t face_map;
            face_map["head"] = coords_t();
            face_map["head"].x = faces[i].x;
            face_map["head"].y = faces[i].y;
            face_map["dimensions"].x = faces[i].width;
            face_map["dimensions"].y = faces[i].height;

            // Detect facial features
            cimg_library::CImg<unsigned char>* cimg_gray = cvImg_to_CImg(image_gray);
            flandmark->detect_optimized(cimg_gray, bbox);
            delete cimg_gray;

            // Facial feature information
            const std::vector<clandmark::Vertex>& vertices = flandmark->getVertices();
            clandmark::fl_double_t* landmarks = flandmark->getLandmarks();
            for(size_t j = 1; j < vertices.size(); j++) {
                face_map[vertices[j].name] = coords_t();
                face_map[vertices[j].name].x = int(landmarks[j*2]);
                face_map[vertices[j].name].y = int(landmarks[(j*2)+1]);
            }
            ret.push_back(face_map);
        }

        /*
         * Cleanup
         */
        delete featurePool;
        delete flandmark;

        return ret;
    }
}
