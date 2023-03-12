"""
This file contains the functions created to answer the first research question.
The functions will create machine learning models to predict the worker's
likely of seeking treatment and will allow to see the correlation of factors.
"""
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn import tree
from IPython.display import Image, display
import graphviz
from sklearn.tree import export_graphviz


def best_test_split(features: pd.DataFrame, labels: pd.Series) -> float:
    """
    Finds the best test split for a given dataset by testing the accuracy of
    the model trained on different test sizes.

    Args:
        features (pd.DataFrame): Features of the dataset.
        labels (pd.Series): Labels of the dataset.

    Returns:
        float: Best test split value.
    """
    best_split = 0
    best_split_score = 0

    for split in np.linspace(0.1, 0.9, num=9):
        X_train, X_test, Y_train, Y_test = \
            train_test_split(features, labels, test_size=split)

        clf = tree.DecisionTreeClassifier()
        clf.fit(X_train, Y_train)
        test_predictions = clf.predict(X_test)

        current_split_score = accuracy_score(Y_test, test_predictions)

        if current_split_score > best_split_score:
            best_split_score = current_split_score
            best_split = split

    if best_split == 0.1 or best_split > 0.4:
        best_split = 0.3

    return best_split


def best_max_depth(X_train: pd.DataFrame, X_test: pd.DataFrame,
                   Y_train: pd.Series, Y_test: pd.Series) -> int:
    """
    Finds the best maximum depth for a decision tree model by testing the
    accuracy of the model trained on different depths.

    Args:
        X_train (pd.DataFrame): Features of the training dataset.
        X_test (pd.DataFrame): Features of the testing dataset.
        Y_train (pd.Series): Labels of the training dataset.
        Y_test (pd.Series): Labels of the testing dataset.

    Returns:
        int: Best maximum depth value.
    """
    best_depth = 0
    best_depth_score = 0

    for d in range(1, 11):
        model = tree.DecisionTreeClassifier(max_depth=d)
        model.fit(X_train, Y_train)
        test_pred = model.predict(X_test)
        current_depth_score = accuracy_score(Y_test, test_pred)

        if current_depth_score > best_depth_score and d > 1:
            best_depth_score = current_depth_score
            best_depth = d

    return best_depth


def plot_tree(model: tree.DecisionTreeClassifier, features: pd.DataFrame,
              labels: pd.Series) -> None:
    """
    Visualizes a given decision tree model.

    Args:
        model (tree.DecisionTreeClassifier): Trained decision tree model.
        features (pd.DataFrame): Features of the dataset.
        labels (pd.Series): Labels of the dataset.
    """
    dot_data = export_graphviz(model, out_file=None,
                               feature_names=features.columns,
                               class_names=labels.unique(),
                               impurity=False,
                               filled=True, rounded=True,
                               special_characters=True)
    graphviz.Source(dot_data).render('tree.gv', format='png')
    display(Image(filename='tree.gv.png'))


def clf_model(df: pd.DataFrame) -> None:
    """
    Creates the "best" Decision Tree model for the instance and
    visualizes the model.

    Args:
        df (pd.DataFrame): A pandas dataframe that contains cleaned data.

    Returns:
        None. This function does not return anything.
        It generates the "best" Decision Tree model for the given dataset
        and visualizes it using graphviz.
    """
    data = df[['Age', 'Country', 'self_employed', 'family_history',
               'no_employees', 'tech_company', 'wellness_program',
               'treatment']].dropna()
    features = data.loc[:, data.columns != 'treatment']
    features = pd.get_dummies(features)
    labels = data['treatment']

    best_split = best_test_split(features, labels)
    X_train, X_test, Y_train, Y_test = \
        train_test_split(features, labels, test_size=best_split)

    clf = tree.DecisionTreeClassifier()
    clf.fit(X_train, Y_train)

    # Print accuracy
    test_predictions = clf.predict(X_test)
    print('Best Split:', format(round(best_split, 1)),
          'Test  Accuracy:', accuracy_score(Y_test, test_predictions))

    best_depth = best_max_depth(X_train, X_test, Y_train, Y_test)
    # Create an untrained model
    short_clf = tree.DecisionTreeClassifier(max_depth=best_depth)

    # Train it on the **training set**
    short_clf.fit(X_train, Y_train)

    # Print accuracy
    test_predictions = short_clf.predict(X_test)
    print('Best Max Depth:', format(best_depth),
          'Test  Accuracy:', accuracy_score(Y_test, test_predictions))

    plot_tree(short_clf, X_train, Y_train)
