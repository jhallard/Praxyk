#include <praxyk/spam.hpp>
#include <praxyk/paths.hpp>

#include <mlpack/core.hpp>
#include "naive_bayes_classifier.hpp"

using namespace mlpack;
using namespace mlpack::naive_bayes;
using namespace std;
using namespace arma;

namespace praxyk {

/*
 * TODO: serialization. This currently trains the classifier
 * every call.
 */
 float get_spam_chance(const std::string &filename) {
    const string trainingDataFilename = get_mlpack_dir() + "/training.csv";
    mat trainingData;
    data::Load(trainingDataFilename, trainingData, true);

    Col<size_t> labels;
    vec mappings;
    vec rawLabels = trans(trainingData.row(trainingData.n_rows - 1));
    rawLabels.print();
/*    data::NormalizeLabels(rawLabels, labels, mappings);
    // Remove the label row.
    trainingData.shed_row(trainingData.n_rows - 1);

    // Load the file to interpret.
    const string testingDataFilename = filename;

    mat testingData;
    data::Load(testingDataFilename, testingData, true);

    if (testingData.n_rows != trainingData.n_rows){
        Log::Fatal << "Test data dimensionality (" << testingData.n_rows << ") "
        << "must be the same as training data (" << trainingData.n_rows - 1 << ")!"
        << std::endl;
    }
    Timer::Start("training");
    NaiveBayesClassifier<> nbc(trainingData, labels, mappings.n_elem,false);
    Timer::Stop("training");
    Col<size_t> results;
    Timer::Start("testing");
    nbc.Classify(testingData, results);
    Timer::Stop("testing");

    // Un-normalize labels to prepare output.
    vec rawResults;
 //   data::RevertLabels(results, mappings, rawResults);
    // Only return the first result.
 //   return rawResults[0];
 */
    return 12;
}

}
