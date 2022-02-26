import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

def model_function():
    dataset = pd.read_csv('final.csv')

    with open('final.csv', 'r') as fl:
        data = fl.readlines()
    lines = len(list(data))
    lines = lines - 2

    cols = ['personId', 'MaxEducation', 'PrimaryOccupation', 'Stage', 'AnnualIncome', 'leadquality']

    dataset = dataset.fillna(" ")
    dataset.fillna(dataset.mode())

    dataset[cols] = dataset[cols].apply(LabelEncoder().fit_transform)

    X = dataset.iloc[:5646, [1, 2, 3, 4, 5]].values
    y = dataset.iloc[:5646, -1].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)

    st_X = StandardScaler()
    X_train = st_X.fit_transform(X_train)
    X_test = st_X.transform(X_test)

    classifier = KNeighborsClassifier(n_neighbors=7, metric='minkowski', p=2)
    classifier.fit(X_train, y_train)

    predict = classifier.predict(X_test)

    Z = dataset.iloc[-1:, [1, 2, 3, 4, 5]].values
    output = classifier.predict(Z)
    return output


