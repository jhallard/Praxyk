#include <praxyk/spam.hpp>
#include <praxyk/paths.hpp>

#include <mlpack/core.hpp>
#include <floatfann.h> // Needs to be included before fann_cpp.h
#include <fann_cpp.h>
#include "naive_bayes_classifier.hpp"

using namespace mlpack;
using namespace mlpack::naive_bayes;
using namespace std;
using namespace arma;
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
     * This works finally. It trains the classifier every call
     * which is suboptimal. Serialization upcoming.
     */
     float get_spam_chance(const std::string &filename) {
      const string trainingDataFilename = get_mlpack_dir() + "/training.csv";
      mat trainingData;
      data::Load(trainingDataFilename, trainingData, true);

      Col<size_t> labels;
      vec mappings;
      vec rawLabels = trans(trainingData.row(trainingData.n_rows - 1));
      data::NormalizeLabels(rawLabels, labels, mappings);
    // Remove the label row.
      trainingData.shed_row(trainingData.n_rows - 1);

      //load the file to interpret
      const string testingDataFilename = filename;

      mat testingData;
      data::Load(testingDataFilename, testingData, true);

      if (testingData.n_rows != trainingData.n_rows)
        Log::Fatal << "Test data dimensionality (" << testingData.n_rows << ") "
      << "must be the same as training data (" << trainingData.n_rows - 1
        << ")!" << std::endl;

      Timer::Start("training");
      NaiveBayesClassifier<> nbc(trainingData, labels, mappings.n_elem,
      false);
      Timer::Stop("training");
      Col<size_t> results;
      Timer::Start("testing");
      nbc.Classify(testingData, results);
      Timer::Stop("testing");

  // Un-normalize labels to prepare output.
      vec rawResults;
      data::RevertLabels(results, mappings, rawResults);
      //only return the first result
      return rawResults[0];
    }

}
