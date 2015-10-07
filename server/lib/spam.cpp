#include <praxyk/spam.hpp>

#include <fann.h> // Needs to be included before fann_cpp.h
#include <fann_cpp.h>

namespace praxyk {
    static PRAXYK_INLINE FANN::neural_net _init_spam_net() {
        /*
         * The spam training data will be at a specific filepath
         * in the instance. Once this is in-place, this function
         * will create a FANN instance, train it with our spam
         * data, and make it available for use as soon as the
         * library is loaded.
         */
        return FANN::neural_net();
    }

    static FANN::neural_net _nnet = _init_spam_net();

    float get_spam_chance(const std::string &message) {
        return 0.0;
    }
}
