#include <praxyk/spam.hpp>

#include <floatfann.h> // Needs to be included before fann_cpp.h
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

    /*
     * This just shows how the neural net will be called. We
     * still need to figure out how to go from the message
     * we're passing in to the actual input numbers. Given that
     * we're not actually instantiating the neural net, running
     * this will segfault.
     */
    float get_spam_chance(const std::string &message) {
        fann_type dummy_inputs[3];
        dummy_inputs[0] = 1;
        dummy_inputs[1] = 1;
        dummy_inputs[2] = 1;

        return *(_nnet.run(dummy_inputs));
    }
}
