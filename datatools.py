import pandas as pd 
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn import metrics
import matplotlib.pyplot as plt
from tqdm import tqdm

def make_clean_data(pd_data,verbose = False):
    """
    -Given any dataframe, removes rows with nan or none, examining 
    feature by feature 
    -This probably can be done by doing the whole dataframe simultaneously 
    """
    #infer the features we have kept by checking columns of the input dataframe
    
    #Needed: check all features for missing values and remove everybody with missing. 
    #check remaining percentage 
    
    features = pd_data.columns 
    missing_dict = dict()
    # bad_rows = list()

    bad_rows_index = pd_data.isna().sum(axis=1).to_numpy().nonzero()
    bad_feature_index = pd_data.isna().sum().to_numpy().nonzero()
    bad_feature = pd_data.columns[bad_feature_index]

    for ft in bad_feature:
        #Calculate the percentage of that feature which was True under .isnull()
        num_missing_bool = pd_data.isna().sum()[ft]
        missing_dict[ft] =  num_missing_bool  / len(pd_data[ft])

        if verbose:
            print("Issue Feature:\n", ft, '\n', '\n Num of null=', num_missing_bool, '\n\n')
        else:
            pass

    # for ft in features:
    #     pd_data.isna().sum()
    #     feature_series = pd_data[ft]
    #     missing_bool = feature_series.isnull()
    #     bad_indices = feature_series.index[missing_bool]
    #     #Calculate the percentage of that feature which was True under .isnull()
    #     missing_dict[ft] = 100*float(np.sum(missing_bool)/feature_series.shape[0])
    #
    #
    #     if not bad_indices.empty:
    #         if verbose:
    #             print("Issue Feature:\n", ft,'\n', bad_indices, '\n Num of null=', len(bad_indices), '\n\n')
    #             bad_rows += list(bad_indices)
    #             print('Here are Nan Indices:', bad_indices)
    #         else:
    #             pass
            
    #Total percentage(s) of data removed
    if verbose:
        # print('Here are Nan Row Indices:', bad_rows_index[0], '\n') #maybe we don't need but I added here
        print('Total Number of Removed Row Instances = ', len(bad_rows_index[0]),'\n ')
        print('Percentage of Removed Features: \n',missing_dict)
    #Eliminate duplicates and sort 
    # bad_rows = list(set(bad_rows))
    # bad_rows.sort()

    # Get rid of rows containing null or empty
    # clean_data = pd_data.drop(bad_rows)
    clean_data = pd_data.drop(bad_rows_index[0])

    # Check if clean
    assert np.size(clean_data.isna().sum(axis=1).to_numpy().nonzero()[0]) == 0, "Clean data still contains NaN"

    #Check the number of resulting data points 
    # if verbose:
    #     print('Here is shape of original data:',data.shape,'\n\n')
    #     print('Here is shape of the clean data:', data_clean.shape,\
    #           '\n Number of Removed Instances =',len(bad_rows))
        
    return clean_data, missing_dict, bad_rows_index

def select_features(pd_data, which = 'basic'):
    """
    pd_data: should be the raw, completely unprocessed feature data 
    
    which:: <string> - determine which set of features to use. Option: 'basic', 'freq', 'all'
    """
    features = pd_data.columns 
    ft_keep = list()
    
    #Here are the features related to the absolute amount of money; some of them can be used as LABEL
    ft_basic =['BALANCE', 'PURCHASES',
           'ONEOFF_PURCHASES', 'INSTALLMENTS_PURCHASES', 'CASH_ADVANCE',
           'CREDIT_LIMIT', 'PAYMENTS',
           'MINIMUM_PAYMENTS', 'PRC_FULL_PAYMENT']
    #the last one is the percent of full payment being paid

    #Here are the features related to the frequency
    ft_freq= ['BALANCE_FREQUENCY','PURCHASES_FREQUENCY', 'ONEOFF_PURCHASES_FREQUENCY',
           'PURCHASES_INSTALLMENTS_FREQUENCY', 'CASH_ADVANCE_FREQUENCY']

    #Define which features to keep 
    if which =='basic':
        ft_keep = ft_basic[:]
        print('Here are the selected features (related to dollars):\n', ft_basic, '\n')
    if which == 'freq':
        ft_keep = ft_freq[:]
        print('Here are the selected features (related to frequency): \n', ft_freq, '\n')
    elif which == 'all':
        ft_keep = ft_basic[:] + ft_freq[:]
        print('Here are the selected features (all of them): \n', ft_keep, '\n')
    print('Features retained are: '+which+'\n')
    
    #Here are the features haven't been used
    ft_unused = set(list(features))-set(ft_keep)
    ft_unused = list(ft_unused)

    # print('Here are the features related to dollars:\n', ft_basic,'\n')
    # print('Here are the features related to frequency: \n',ft_freq,'\n')
    print('Here are the features not used: \n', ft_unused)
    
    #Now slice the data according to the desired features
    keep_data = pd_data[ft_keep]

    return keep_data, ft_keep[:], list(ft_unused)

def remove_quantiles(pd_data,p = 1):
    percentile = p
    quantile = percentile / 100 
    remove_indices = list()
    # feature_stats = dict()
    
    for feature in pd_data.columns:
        feature_series = pd_data[feature]
        quantile_filter = np.quantile(feature_series,[quantile,1-quantile])
        feature_outside = feature_series[(feature_series < quantile_filter[0]) | (feature_series > quantile_filter[1])]
        # outside_indices = feature_outside.index
        remove_indices += list(feature_outside.index)
    remove_indices = list(set(remove_indices))
    remove_indices.sort()
    
    pd_data_reduced = pd_data.drop(remove_indices)
    
    #Calculate what percent of total data is captured in these indices
    percent_removed = 100*(len(remove_indices)/pd_data.index.shape[0])
    print('Percent of Data Removed Across These Quantiles Is: ', percent_removed)
    
    return pd_data_reduced, percent_removed

def run_svd(pd_data,percent_var = 95):
    """
    :pd_data: the dataframe containing the 'already standardized'] data 
    :percent_var: float - a value between [0,100]
    """
    #add checking if percent_var between 0 and 100 
    
    #Calculate the desired number of SVD components in the decomposition 
    start_rank = (pd_data.shape[-1]-1)
    #Make instance of SVD object class from scikit-learn and run the decomposition 
    #Issue: scikitlearn TruncatedSVD only allows n_components < n_features (strictly)
    SVD = TruncatedSVD(n_components = start_rank)
    SVD.fit(data_clean)
    X_SVD = SVD.transform(data_clean)
    
    #Wrap the output as a dataframe 
    X_SVD = pd.DataFrame(X_SVD,columns = ['Singular Component '+str(i+1) for i in range(X_SVD.shape[-1])])
    
    #Calculate the number of components needed to reach variance threshold 
    var_per_comp = SVD.explained_variance_ratio_
    
    #Calculate the total variance explainend in the first k components 
    total_var = 100*np.cumsum(var_per_comp)
    print('------------- SVD Output ----------------')
    print('Percent Variance Explained By First '+str(start_rank)+' Components: ',total_var,'\n\n')
    #rank = np.nonzero(total_var>=var_threshold)[0][0]+1
    rank = (next(x for x, val in enumerate(total_var) if val > percent_var))
    rank += 1
    
    if rank == 0: 
        print('No quantity of components leq to '+str(start_rank+1)+' can explain '+str(percent_var)+'% variance.')
    else:
        print(str(total_var[rank-1])+'% variance '+'explained by '+str(rank)+' components. '+\
              'Variance Threshold Was '+str(percent_var)+'.\n\n')
    
    return X_SVD, rank, percent_var, total_var

def data_quantization(pd_data, scale =10):
    """
    Quantize a panda data frame into integer with new features according to the given scale.
    e.g. if scale = 10: the new feature assign label 1 to the
    :param pd_data:
    :param scale:
    :return: data_quantile: the quantized data
             percent_of_zero: at least that much percent of feature are zeros
    """
    p = np.linspace(0, scale, scale+1) * 0.1
    data_quantile = pd_data.copy()
    percent_of_zero = {}
    eps = 1e-5

    for feature in pd_data.columns:
        feature_new = feature + '_QUANTILE'
        data_quantile[feature_new] = 0

        for (i, quantile) in enumerate(p[:-1]):
            quantile_filter = np.quantile(pd_data[feature], [quantile, p[i + 1]])
            data_quantile.loc[((pd_data[feature] > quantile_filter[0]) &
                                       (pd_data[feature] <= quantile_filter[1])), feature_new] = i+1

            if i == 0 and quantile_filter[0] > 0:  # deal with 0-quantile being non-zero
                data_quantile.loc[((pd_data[feature] >= quantile_filter[0]) &
                                       (pd_data[feature] <= quantile_filter[1])), feature_new] = i+1

            if quantile_filter[0] <= eps and quantile_filter[1] >= eps:
                percent_of_zero[feature] = quantile
            elif quantile_filter[0] > eps and i == 0:
                percent_of_zero[feature] = 0

        data_quantile.drop(columns = feature, axis = 1, inplace=True)
    return data_quantile, percent_of_zero

def get_elbow_index(scores, cluster_step = 1):
    #Calculate derivative of cluster scores assuming a uniform step size
    
    #First derivative condition 
    diff = (1/cluster_step)*scores[1:len(scores)]-scores[0:len(scores)-1]
    res = next(x for x, val in enumerate(diff) if val > -1)
    #diff2 = (1/cluster_step)*diff[1:len(scores)]-diff[0:len(scores)-1]
    
    return res 

def elbow_method(X, k_search, method = 'KMeans', plot = True):
    """
    Elbow Method for different clustering methods with all metrics shown
    :param X: (np,ndarray NxD) data matrix 
    :param k_search: (np.ndarray) list containing the number of clusters to compare over
    :param method: (string) "Kmeans" or "GM" specify the clustering techniques
    :param plot: (boolean) if plotting the results or not
    :return: 
    """
    #ksearch must be linear for this to work 
    cluster_diff = k_search[1]-k_search[0]
    
    silh_score = np.zeros(len(k_search))
    CHindex_score = silh_score.copy()
    DBindex_score = silh_score.copy()
    SoS = silh_score.copy()
    
    if method == 'KMeans' or method == 'GM':
        pass
    else:
        raise ValueError('method is not a valid method (only "kmeans" or "gm" is available)')
    # if method == "kmeans":
    #     SoS = silh_score.copy()
    SoS = silh_score.copy()
    print("Running Elbow Method...")
    for (i, k) in tqdm(enumerate(k_search), total=len(k_search)):
        if method == 'KMeans':
            kmeans = KMeans(n_clusters=int(k), random_state=0).fit(X)
            kmeans_label = kmeans.labels_
            SoS[i] = kmeans.inertia_
            silh_score[i] = metrics.silhouette_score(X, kmeans_label, metric='euclidean')
            CHindex_score[i] = metrics.calinski_harabasz_score(X, kmeans_label)
            DBindex_score[i] = metrics.davies_bouldin_score(X, kmeans_label)
        elif method == 'GM':
            gm = GaussianMixture(n_components=int(k), random_state=0).fit(X)
            gm_label = gm.predict(X)
            silh_score[i] = metrics.silhouette_score(X, gm_label, metric='euclidean')
            CHindex_score[i] = metrics.calinski_harabasz_score(X, gm_label)
            DBindex_score[i] = metrics.davies_bouldin_score(X, gm_label)

    metric_list = [silh_score/np.max(np.abs(silh_score)), CHindex_score/np.max(np.abs(CHindex_score)),
                   DBindex_score/np.max(np.abs(DBindex_score)), SoS/(max(np.max(SoS),0.1))]
    
    metric_legend = ['Silhouette', 'CHindex', 'DBindex', 'SoS']
    
    elbow_index = get_elbow_index(metric_list[-1])
    ssq_optimal_K = k_search[elbow_index]
    
    if plot:
        if method == 'KMeans':
            m = 4
        elif method == 'GM':
            m = 3
        # plt.figure()
        # plt.figure(figsize=(6, 6))
        Markers = ['+', 'o', '*', 'x']
        for i in range(m):
            plt.plot(k_search, metric_list[i], marker = Markers[i])
        plt.xlabel(r'Number of clusters $k$', fontsize=20, fontname="Times New Roman", fontweight='bold')
        plt.ylabel('Metric Score (Normalized)', fontsize=20, fontname="Times New Roman", fontweight='bold')
        plt.title('Evaluation of {} clustering'.format(method), fontsize=22, fontweight='bold')
        plt.legend(metric_legend, loc='best')
        plt.show()
    return





if __name__ == "__main__":
    
    pass 