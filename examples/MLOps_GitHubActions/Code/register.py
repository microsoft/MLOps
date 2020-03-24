import os
import re
import json
import azureml
import argparse
from pathlib import Path
from shutil import copyfile
from azureml.core.run import Run
from azureml.core.model import Model

def info(msg, char = "#", width = 75):
    print("")
    print(char * width)
    print(char + "   %0*s" % ((-1*width)+5, msg) + char)
    print(char * width)

def best_model(source_path):
    best_model = None
    maxsum = -1
    for file in Path(source_path).glob('*.hdf5'):
        ps = [float(p.group()[1:]) for 
                p in re.finditer(r'\D\d\.\d\d', str(file))]
        # incorrect format
        if len(ps) == 0: continue
        sm = ps[0] + ps[1]
        # look at train/val acc combo
        if sm > maxsum:
            best_model = {
                'file': file,
                'train': ps[0],
                'val': ps[1],
                'sum': ps[0] + ps[1]
            }
            maxsum = sm
            
    return best_model
    

def main(run, source_path, target_path, build):
    # load previous step metadata
    train_step = os.path.join(source_path, 'metadata.json')
    with open(train_step) as f:
        train = json.load(f)

    for i in train:
        print('{} => {}'.format(i, train[i]))

    metadata_file = 'metadata.json'
    model_file = 'model.hdf5'
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    info('Model')
    model = best_model(source_path)
    print('Best model found:')
    for i in model:
        print('   {} => {}'.format(i, model[i]))

    target_model = os.path.join(target_path, model_file)
    copyfile(str(model['file']), target_model)
    
    target_metadata = os.path.join(target_path, metadata_file)
    copyfile(os.path.join(source_path, metadata_file), target_metadata)

    original_file = str(model['file'].relative_to(source_path))
    print('Original File: {}'.format(original_file))

    # not offline - we can register in AML
    if not run.id.lower().startswith('offlinerun'):
        info('Register')

        # for tagging build number associated with build
        model['github_ref'] = build
        model['file'] = original_file
        print(f'Uploading {target_path} to run {run.id} as the "model" folder')

        run.upload_folder('modelfiles', target_path)
        m = run.register_model(model_name='seer', model_path='modelfiles', tags=model)
        print(m)
        

    print('Done!')

if __name__ == "__main__":
    # argparse stuff for model path and model name
    parser = argparse.ArgumentParser(description='Model Registration Process')
    parser.add_argument('-s', '--source_path', help='directory to generated models', default='data/train')
    parser.add_argument('-t', '--target_path', help='write directory', default='data/model')
    parser.add_argument('-b', '--build', help='build identifier', default='1.0.0')
    args = parser.parse_args()

    run = Run.get_context()
    offline = run.id.startswith('OfflineRun')
    print('AML Context: {}'.format(run.id))
    
    info('Input Arguments')
    params = vars(args)
    for i in params:
        print('{} => {}'.format(i, params[i]))
        if not offline:
            run.log(i, params[i])

    params['run'] = run

    main(**params)
