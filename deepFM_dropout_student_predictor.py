"""deepFM_dropout_student_predictor modified original.ipynb

Original file is located at
    https://colab.research.google.com/drive/1g758nsom_RDisB2Pdd2UX6nuLkgvkPiK

**Loading libraries**
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from keras.layers import Input, Dense, Lambda, Subtract
from keras.models import Model
import keras.backend as K

"""mounting google drive to read data file

**converting csv file into pandas data frame**
"""

dataset = pd.read_csv("/content/dataset.csv")
dataset.head()

# Assuming 'dataset' is your Pandas DataFrame

# Filter out instances with "Enrolled" in the Target class
dataset = dataset[dataset['Target'] != 'Enrolled']

# Optional: Reset the index if needed
dataset = dataset.reset_index(drop=True)

dataset.shape

dataset.info()

dataset["Target"].value_counts()

sns.countplot(x=dataset["Target"])

sns.countplot(x=dataset["Gender"])

dataset["Displaced"].value_counts()

"""**columns name**"""

dataset.columns

"""**Null enteries**"""

dataset.isnull().sum()

"""**checking repeated columns**"""

dataset.columns.value_counts()

top_handles = dataset.Course.value_counts().sort_values(ascending=False)
top_handles.head(30).plot.barh(title='Top 30 Courses of users',
                               figsize=(6,6),color="blue")

"""**EDA**"""

dataset.shape

dataset.isnull()

dataset.info()

dataset.head()

# Create a contingency table
cont_table = pd.crosstab(dataset['Marital status'], dataset['Target'])

# Visualize the contingency table as a heatmap
sns.heatmap(cont_table, cmap='coolwarm', annot=True, fmt='d')

dataset.info()

classes = dataset['Target'].copy()
features = dataset.drop(['Target'], axis=1)

label_mapping = {'Graduate': 1, 'Dropout': 0, 'Enrolled':2}  # You can adjust the mapping as needed

# Convert categorical labels to numeric using the mapping dictionary
dataset['Target_numeric'] = dataset['Target'].map(label_mapping)

classes2 = dataset['Target_numeric'].copy()

features.head()

classes2.head()

from sklearn.model_selection import train_test_split

!pip install deepctr

import pydotplus
from IPython.display import Image
from graphviz import Digraph

# Create a directed graph
dot = Digraph(comment='DeepFM-Based Predictive Model for Student Dropout in Online Classes')

# Add nodes to the graph
dot.node('data_preprocessing', 'Data Preprocessing')
dot.node('data_splitting', 'Data Splitting')
dot.node('model_design', 'DeepFM Model Design')
dot.node('model_training', 'Model Training')
dot.node('model_evaluation', 'Model Evaluation')

# Add edges to the graph
dot.edge('data_preprocessing', 'data_splitting')
dot.edge('data_splitting', 'model_design')
dot.edge('model_design', 'model_training')
dot.edge('model_training', 'model_evaluation')

# Create a PydotPlus graph from the Digraph
graph = pydotplus.graph_from_dot_data(dot.source)

# Display the image of the graph
Image(graph.create_png())

import pydotplus
from IPython.display import Image
from graphviz import Digraph

# Create a directed graph
dot = Digraph(comment='DeepFM-Based Predictive Model')

# Add nodes to the graph
dot.node('input_layer', 'Input Layer')
dot.node('embedding_layer', 'Embedding Layer')
dot.node('fm_layer', 'FM Layer')
dot.node('dnn_layer', 'DNN Layer')
dot.node('output_layer', 'Output Layer')

# Add edges to the graph
dot.edge('input_layer', 'embedding_layer')
dot.edge('embedding_layer', 'fm_layer')
dot.edge('fm_layer', 'dnn_layer')
dot.edge('input_layer', 'dnn_layer')
dot.edge('dnn_layer', 'output_layer')

# Create a PydotPlus graph from the Digraph
graph = pydotplus.graph_from_dot_data(dot.source)

# Display the image of the graph
Image(graph.create_png())

!pip install tensorflow==2.10.0

from deepctr.models import DeepFM

from deepctr.feature_column import SparseFeat,DenseFeat, get_feature_names

df = dataset
# separate the target variable (if applicable)
target = df['Target']
df = df.drop('Target', axis=1)
scaler = StandardScaler()
df=scaler.fit_transform(df)

# train_data = train_data.astype('float32')
# y_train.values = y_train.values.astype('float32')
# test_data = test_data.astype('float32')
# y_test.values = y_test.values.astype('float32')
df = dataset
df['Target_numeric'] = df['Target_numeric'].values.astype('float32')

df.head()

df = dataset
# separate the target variable (if applicable)
target = df['Target_numeric']

df = df.drop('Target', axis=1)

df = df.drop('Target_numeric', axis=1)
scaler = StandardScaler()
df=scaler.fit_transform(df)

df = pd.DataFrame(data=df, columns=[f"PC{i+1}" for i in range(df.shape[1])])

df['labels'] = target

df.head()

target_col = 'labels'
feature_cols = df.columns.drop(target_col)

x_train, x_test, y_train, y_test = train_test_split(df[feature_cols], df[target_col], test_size=0.01, random_state=42)

dense_feats = [DenseFeat(feat, 1) for feat in x_train.select_dtypes('number').columns]
sparse_feats = []

linear_cols = sparse_cols = dense_feats + sparse_feats
dnn_cols = dense_feats + sparse_feats

train_data = {feat: x_train[feat].values.reshape(-1, 1) for feat in x_train.columns}
test_data = {feat: x_test[feat].values.reshape(-1, 1) for feat in x_test.columns}

model = DeepFM(linear_cols, dnn_cols, task='binary')

# Compile the model
model.compile("adam", "binary_crossentropy", metrics=['accuracy'])

features.head()



# Train the model
history = model.fit(train_data, y_train.values, batch_size=64, epochs=20, validation_data=(test_data, y_test.values))

print(f"Type of train_data: {type(train_data)}")
print(f"Type of y_train.values: {type(y_train.values)}")
print(f"Type of test_data: {type(test_data)}")
print(f"Type of y_test.values: {type(y_test.values)}")

# train_data = train_data.astype('float32')
# y_train.values = y_train.values.astype('float32')
# test_data = test_data.astype('float32')
# y_test.values = y_test.values.astype('float32')

"""**Training and validation curves**"""

# Assuming 'history' contains the training history
epochs = range(1, len(history.history['accuracy']) + 1)

# Plot training and validation accuracy
plt.plot(epochs, history.history['accuracy'], label='Train Accuracy')
plt.plot(epochs, history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy over Epochs')
plt.legend()
plt.show()

# epochs = list(range(50))
# acc = history.history['accuracy']
# val_acc = history.history['val_accuracy']

# plt.plot(epochs, acc, label='train accuracy')
# plt.plot(epochs, val_acc, label='val accuracy')
# plt.xlabel('epochs')
# plt.ylabel('accuracy')
# plt.legend()
# plt.show()

loss = history.history['loss']
val_loss = history.history['val_loss']

plt.plot(epochs, loss, label='train loss')
plt.plot(epochs, val_loss, label='val loss')
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend()
plt.show()

ypred=model.predict(test_data)

ypred = (ypred>0.5).astype(int)

from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn import metrics

# Commented out IPython magic to ensure Python compatibility.
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt
# %matplotlib inline

"""**confusion matrix**"""



cm = confusion_matrix(y_test.values, ypred)
sns.heatmap(cm, annot=True, fmt="d")

from sklearn.metrics import precision_score, recall_score

from sklearn.metrics import precision_score, recall_score, classification_report

# Assuming ypred and y_test.values are defined
precision = precision_score(y_test.values, ypred, average='weighted')  # You can choose 'micro', 'macro', 'weighted', or 'samples'
recall = recall_score(y_test.values, ypred, average='weighted')  # You can choose 'micro', 'macro', 'weighted', or 'samples'

print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")

# Alternatively, you can use classification_report for a detailed report
report = classification_report(y_test.values, ypred)
print(report)
