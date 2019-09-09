
import numpy as np
import pandas as pd

# function to reshape features into (samples, time steps, features) 

def gen_sequence(id_df, seq_length, seq_cols):
    """ Only sequences that meet the window-length are considered, no padding is used. This means for testing
    we need to drop those which are below the window-length. An alternative would be to pad sequences so that
    we can use shorter ones """
    data_array = id_df[seq_cols].values
    num_elements = data_array.shape[0]
    
    for start, stop in zip(range(0, num_elements-seq_length), range(seq_length, num_elements)):
        
        yield data_array[start:stop, :]
        
# function to generate labels
def gen_labels(id_df, seq_length, label):
    data_array = id_df[label].values
    num_elements = data_array.shape[0]
    return data_array[seq_length:num_elements, :]


def extract_features(input_cols):
    # pick the feature columns 
    sequence_cols = ['setting1', 'setting2', 'setting3', 'cycle_norm']
    key_cols = ['engine_id', 'cycle']
    label_cols = ['label1', 'label2', 'RUL']

    
    sensor_cols = [x for x in input_cols if x not in set(key_cols)]
    sensor_cols = [x for x in sensor_cols if x not in set(label_cols)]
    sensor_cols = [x for x in sensor_cols if x not in set(sequence_cols)]

    # The time is sequenced along
    # This may be a silly way to get these column names, but it's relatively clear
    sequence_cols.extend(sensor_cols)
    
    return sequence_cols

def to_tensors_imp(df, timestep, is_test):
    
   
    input_features = extract_features(df.columns.tolist())
    if is_test == True:
        return tensorize_test_set(df, input_features, timestep)
    
    # generator for the sequences for training set
    seq_gen = (list(gen_sequence(df[df['engine_id']==id], timestep, input_features)) 
               for id in df['engine_id'].unique())

    # generate sequences and convert to numpy array

    X = np.concatenate(list(seq_gen)).astype(np.float32)


    # generate labels
    label_gen = [gen_labels(df[df['engine_id']==id], timestep, ['label1']) 
                 for id in df['engine_id'].unique()]
    y = np.concatenate(label_gen)

    y = y.reshape(-1)
    
    return X,y

def tensorize_test_set(test_df, input_features,timestep):
    seq_array_test_last = [] 
    engine_ids = []
    
    for id in test_df['engine_id'].unique():
        if len(test_df[test_df['engine_id']==id]) >= timestep:
            seq_array_test_last.append(test_df[test_df['engine_id']==id][input_features].values[-timestep:])
            engine_ids.append(id)

    X = np.asarray(seq_array_test_last).astype(np.float32)
    y_mask = [len(test_df[test_df['engine_id']==id]) >= timestep for id in test_df['engine_id'].unique()]
    y = test_df.groupby('engine_id')['label1'].nth(-1)[y_mask].values
    y = y.reshape(-1)
    
    return X,y,engine_ids


def to_tensors(df_path, is_test = False):
    '''
     Converts dataset to numpy tensors
     
     params:
         df_path: path to csv data file
         is_test: testing set being passed default to false
         
     return X (m,50,25), y (m,), 
            engine_Ids: list if test set
    '''
    
    timestep = 50
    df = pd.read_csv(df_path)
    return to_tensors_imp(df, timestep, is_test)
