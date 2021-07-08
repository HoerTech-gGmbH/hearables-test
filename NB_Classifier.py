def NB(partic):
    # inspired by https://www.datacamp.com/community/tutorials/naive-bayes-scikit-learn
    import matplotlib.pyplot as plt
    import numpy as np
    from sklearn import preprocessing  # Import LabelEncoder
    from sklearn.naive_bayes import GaussianNB  # Import Gaussian Naive Bayes model
    from sklearn.metrics import confusion_matrix
    from matplotlib.ticker import MultipleLocator
    from sklearn.model_selection import StratifiedKFold

    # Input is an array of several cofusion matrices, namely as many as we define folds in our classification.
    # This function averages the conf. matrices and plots the mean cm.
    # check out https://towardsdatascience.com/demystifying-confusion-matrix-confusion-9e82201592fd for further explanations
    def my_plot(cm, splits):
        # max number of detections over splits
        max_tp = cm.max()
        # average the matrices from every fold
        cm_mean = cm.mean(axis=0)
        # normalize by max number of true positives throughout all folds
        cm_mean = (cm_mean / max_tp) * 100
        # print(cm_mean)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cax = ax.matshow(cm_mean)
        plt.title('Confusion Matrix of N=1, ' + str(splits) + '-fold Cross Validation')
        fig.colorbar(cax)
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.show()
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.yaxis.set_major_locator(MultipleLocator(1))

    ############## k - fold
    def my_classification(data, labels, splits):
        model = GaussianNB()
        X = data
        y = labels
        splits = splits
        kf = StratifiedKFold(n_splits=splits)
        # kf.get_n_splits(X)  # returns the number of splitting iterations of the cross-validator
        # print(kf)

        # we save the confusion matrix of every run in this array
        cm = np.zeros((splits, np.size(np.unique(y)), np.size(np.unique(y))))
        scores = np.zeros(splits)
        i = 0
        for train_index, test_index in kf.split(X, y):
            # take a subsample of the training and test data and use it for training
            feature_train, feature_test = X[train_index], X[test_index]
            label_train, label_test = y[train_index], y[test_index]
            model.fit(feature_train, label_train)
            scores[i] = model.score(feature_test, label_test)
            print(confusion_matrix(label_test, model.predict(feature_test)))
            cm[i] = confusion_matrix(label_test, model.predict(feature_test))
            i += 1

        # plot_confusion_matrix(cm[1], activity_encoded, "test")
        my_plot(cm, splits)
        print("Average accuracy across " +
              str(splits) +
              " folds for all activities: " +
              str(np.mean(scores)))

    # load features that were created in .... ?
    dataset = np.load(str(partic + 'meanfeatures.npy'), allow_pickle=True).item()
    original = dataset

    # encode activities as numerical labels
    le = preprocessing.LabelEncoder()  # creating labelEncoder
    activity_encoded = le.fit_transform(dataset['activity'])  # Converting string labels into numbers.
    all_labels_ = dataset['activity'];
    del dataset['activity']

    # put everything in matrix with correct size
    Features = list(dataset.keys())
    N = np.size(Features)  # number of features
    M = np.size(dataset[Features[0]])  # number of samples per feature
    Matrix = np.zeros((M, N))
    for j in range(N):  # create numpy array containing all the features
        Matrix[:, j] = dataset[Features[j]]

    my_classification(Matrix, activity_encoded, 5)

    #
    # label_pred = model.predict(X_test)  # Predict the response for test dataset
    # print("Accuracy for AI:",
    #       metrics.accuracy_score(y_test, label_pred))  # Model Accuracy, how often is the classifier correct?
    #

