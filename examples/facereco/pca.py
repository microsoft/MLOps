
import argparse
import numpy as np
import os.path
from sklearn.decomposition import PCA
from sklearn.externals import joblib
from azureml.core.run import Run

def project_to_latent_space(vggface_path, pca_path):
    """
        Part 2a of the paper where we project VGG-face extracted features
        to latent dimensional space using PCA       
    """
    
    X = np.load(os.path.join(vggface_path, 'X.npy'))
    
    nb_components = 40
    pca = PCA(nb_components).fit(X) 
    X_transformed = pca.transform(X) 
    np.save(os.path.join(pca_path, 'X_latent.npy'), X_transformed)
    
    
    # save model to run
    run = Run.get_submitted_run()
    model_filepath = os.path.join(pca_path, 'pca.pkl')
    
    joblib.dump(pca, model_filepath)
    run.upload_file('pca.pkl',model_filepath)
    run.register_model(model_name = "pca.pkl", model_path = "pca.pkl")
    
    # track explained variance per number of principal components in run
    
    exp_variance = np.cumsum(np.round(pca.explained_variance_ratio_, decimals=4)*100)
    run = Run.get_submitted_run()
    run.log_list('Explained variance', exp_variance.tolist())

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--vggface_path')
    parser.add_argument('--pca_path')
    
    vggface_path = parser.parse_args().vggface_path
    pca_path = parser.parse_args().pca_path
    os.makedirs(pca_path, exist_ok=True)
    
    project_to_latent_space(vggface_path, pca_path)