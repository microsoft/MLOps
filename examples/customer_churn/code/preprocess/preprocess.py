import argparse
import pandas as pd
import numpy as np
import os.path
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


def preprocess(input_path):


    """preprocess data set: 
                drop uneeded features
                one hot encode categorical features

         
        Args:
            input_path(str):path to dataset

        return:
            processed dataframe

        """
    df = pd.read_csv(input_path)
    print(df.head())

    df = df.drop_duplicates()

    df[['year','month']] = df[['year','month']].astype('object')
    df.drop(['year','month','customerid'],inplace=True, axis = 1)

    cat_cols = df.select_dtypes(include=['object','category']).columns
    num_cols = set(df.columns) - set(cat_cols)

    df = pd.get_dummies(data=df,
                        columns=cat_cols,
                        prefix='oh_')   

    return df 


def to_normed_tensors(df,seed=129):

    """scale & convert dataframe to training/testing numpy tensors

         
        Args:
            df(dataframe):processed dataframe

        return:
            processed dataframe

    """

    label ='churn'
    X = df.loc[:, ~df.columns.isin([label])].values
    y = df[label].values

    scaler =StandardScaler()
    X = scaler.fit_transform(X)
    print(X.shape, y.shape,sep='\n')
    

    X_train,X_test,y_train,y_test = train_test_split(X,
                                                     y, 
                                                     test_size=.33, 
                                                     random_state=seed)

                                                    
    return  (X_train,X_test,y_train,y_test)


if __name__ == '__main__':

    

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path')
    parser.add_argument('--output_path')
    

    input_path = os.path.join(parser.parse_args().input_path)
    output_path = parser.parse_args().output_path
    
   
    print("reading from", input_path)
    file_name = os.path.join(input_path, 'CATelcoCustomerChurnTrainingSample.csv')
    df = preprocess(file_name)
    X_train,X_test,y_train,y_test = to_normed_tensors(df)

    os.makedirs(output_path, exist_ok = True)
    print('writing to ', output_path)
     
    tensors_lst =[X_train,X_test,y_train,y_test] 
    file_names = ['X_train.npy','X_test.npy','y_train.npy','y_test.npy']

    for file_name,tensors in zip(file_names,tensors_lst):
        file_name = os.path.join(output_path,file_name)
        print("saving",file_name, tensors.shape)
        np.save(file_name,tensors)