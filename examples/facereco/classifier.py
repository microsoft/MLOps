
import argparse
import numpy as np
import os.path
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_validate
from sklearn.externals import joblib
from azureml.core.run import Run

def fit_classifier(vggface_path,pca_path, output_path):
    """
        Part 2b of the paper where we fit classifer on   
            latent matrix       
    """
    
    X = np.load(os.path.join(pca_path, 'X_latent.npy'))
    y = np.load(os.path.join(vggface_path, 'y.npy'))
    
    run = Run.get_submitted_run()
    
    knn = KNeighborsClassifier()
    cv_results = cross_validate(knn, X, y, scoring=['accuracy'], cv=5,
                             verbose=1, return_train_score=True,
                             n_jobs = 1)
    
    # track train accuracy in run
   
    train_accuracy = round(np.mean(cv_results['train_accuracy']),2)
    run.log("mean training accuracy", train_accuracy)  
    
    test_accuracy = round(np.mean(cv_results['test_accuracy']),2)
    run.log("mean testing accuracy", test_accuracy)
    
    # register model to run
    model_filepath = os.path.join(output_path, 'classifier.pkl')  
    joblib.dump(knn, model_filepath)
    run.upload_file('classifier.pkl',model_filepath)
    run.register_model(model_name = 'classifier.pkl', model_path = 'classifier.pkl')

    
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--vggface_path')
    parser.add_argument('--pca_path')
    parser.add_argument('--clf_path')
    
    pca_path = parser.parse_args().pca_path
    vggface_path = parser.parse_args().vggface_path
    output_path = parser.parse_args().clf_path
    os.makedirs(output_path, exist_ok=True)
    
    np.random.seed(123)
    fit_classifier(vggface_path,pca_path, output_path)