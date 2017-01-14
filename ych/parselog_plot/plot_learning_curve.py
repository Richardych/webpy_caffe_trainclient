import os
import sys
import subprocess
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib import pylab as plt
plt.style.use('ggplot')

caffe_path = '/home/deepglint/caffe/'
model_log_path = sys.argv[1]
learning_curve_path = sys.argv[2]

model_log_dir_path = os.path.dirname(model_log_path)
os.chdir(model_log_dir_path)

#Read training and test logs
train_log_path = model_log_path + '.train'
test_log_path = model_log_path + '.test'
train_log = pd.read_csv(train_log_path, delimiter=',')
test_log = pd.read_csv(test_log_path, delimiter=',')

fig, ax1 = plt.subplots()
#Plotting training and test losses
train_loss, = ax1.plot(train_log['NumIters'], train_log['loss'], color='red',  alpha=.5)
test_loss, = ax1.plot(test_log['NumIters'], test_log['loss'], linewidth=2, color='green')
ax1.set_ylim(ymin=0, ymax=1)
ax1.set_xlabel('Iterations', fontsize=15)
ax1.set_ylabel('Loss', fontsize=15)
ax1.tick_params(labelsize=15)
#Plotting test accuracy
ax2 = ax1.twinx()
test_accuracy, = ax2.plot(test_log['NumIters'], test_log['accuracy'], linewidth=2, color='blue')
ax2.set_ylim(ymin=0, ymax=1)
ax2.set_ylabel('Accuracy', fontsize=15)
ax2.tick_params(labelsize=15)
#Adding legend
plt.legend([train_loss, test_loss, test_accuracy], ['Training Loss', 'Test Loss', 'Test Accuracy'], loc='best')
plt.title('Training Curve', fontsize=18)
#Saving learning curve
plt.savefig(learning_curve_path)


