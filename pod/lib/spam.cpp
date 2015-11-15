    #include <praxyk/spam.hpp>
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
     * This just shows how the neural net will be called. We
     * still need to figure out how to go from the message
     * we're passing in to the actual input numbers. Given that
     * we're not actually instantiating the neural net, running
     * this will segfault.
     */
     float get_spam_chance(const std::string &message) {
      return 0.5;
      
  }


  int test(int argc, char* argv[])
  {
      CLI::ParseCommandLine(argc, argv);

  // Check input parameters.
      const string trainingDataFilename = CLI::GetParam<string>("train_file");
      mat trainingData;
      data::Load(trainingDataFilename, trainingData, true);

  // Normalize labels.
      Col<size_t> labels;
      vec mappings;

  // Did the user pass in labels?
      const string labelsFilename = CLI::GetParam<string>("labels_file");
      if (labelsFilename != "")
      {
    // Load labels.
        mat rawLabels;
        data::Load(labelsFilename, rawLabels, true, false);

    // Do the labels need to be transposed?
        if (rawLabels.n_rows == 1)
          rawLabels = rawLabels.t();

      data::NormalizeLabels(rawLabels.unsafe_col(0), labels, mappings);
  }
  else
  {
    // Use the last row of the training data as the labels.
    Log::Info << "Using last dimension of training data as training labels."
    << std::endl;
    vec rawLabels = trans(trainingData.row(trainingData.n_rows - 1));
    data::NormalizeLabels(rawLabels, labels, mappings);
    // Remove the label row.
    trainingData.shed_row(trainingData.n_rows - 1);
}

const string testingDataFilename = CLI::GetParam<std::string>("test_file");
mat testingData;
data::Load(testingDataFilename, testingData, true);

if (testingData.n_rows != trainingData.n_rows)
    Log::Fatal << "Test data dimensionality (" << testingData.n_rows << ") "
<< "must be the same as training data (" << trainingData.n_rows - 1
    << ")!" << std::endl;

    const bool incrementalVariance = CLI::HasParam("incremental_variance");

  // Create and train the classifier.
    Timer::Start("training");
    NaiveBayesClassifier<> nbc(trainingData, labels, mappings.n_elem,
      incrementalVariance);
    Timer::Stop("training");

  // Time the running of the Naive Bayes Classifier.
    Col<size_t> results;
    Timer::Start("testing");
    nbc.Classify(testingData, results);
    Timer::Stop("testing");

  // Un-normalize labels to prepare output.
    vec rawResults;
    data::RevertLabels(results, mappings, rawResults);

  // Output results.  Don't transpose: one result per line.
    const string outputFilename = CLI::GetParam<string>("output");
    data::Save(outputFilename, rawResults, true, false);
    return 0;
}




}
