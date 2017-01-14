#!/usr/bin/env python

import os
import re
import argparse
import csv
from collections import OrderedDict

def Parse_Args():
    description = ('Parse a Caffe training log into two CSV files')
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('logfile_path',help='Path to log file')
    parser.add_argument('output_dir', help='Directory in which to place output CSV files')
    parser.add_argument('--delimiter', default=',', help=('Column delimiter in output files (default: \'%(default)s\')'))
    args = parser.parse_args()
    return args

def Fix_Initial_None(dict_list, isTrain):
    if len(dict_list) > 1:
        dict_list[0]['LearningRate'] = dict_list[1]['LearningRate']
    if len(dict_list) < 1:
	if isTrain:
	    row = OrderedDict([
		('NumIters', '0'),
		('LearningRate', '0.0'),
		('loss', '0.0')
		])
	    dict_list.append(row)
	else:
	    row = OrderedDict([
		('NumIters', '0'),
		('LearningRate', '0.0'),
		('accuracy','0.0'),
		('loss', '0.0')
		])
	    dict_list.append(row) 

def Parse_Line_For_Output(regex_obj, row, row_dict_list, line, iteration, learning_rate):
    output_match = regex_obj.search(line)
    if output_match:
        if not row or row['NumIters'] != iteration:
            if row:
                row_dict_list.append(row)
            row = OrderedDict([
                ('NumIters', iteration),
                ('LearningRate', learning_rate)
            ])
        output_name = output_match.group(2)
        output_val = output_match.group(3)
        row[output_name] = float(output_val)

    if row and len(row_dict_list) >= 1 and len(row) == len(row_dict_list[0]):
        row_dict_list.append(row)
        row = None
    return row_dict_list, row


def Parse_Log(path_to_log):
    regex_weight_decay = re.compile('weight_decay: ([\.\deE+-]+)')
    regex_momentum = re.compile('momentum: ([\.\deE+-]+)')
    regex_power = re.compile('power: ([\.\deE+-]+)')
    regex_gamma = re.compile('gamma: ([\.\deE+-]+)')
    regex_lr_policy = re.compile('lr_policy: \"(.*?)\"')
    regex_max_iter = re.compile('max_iter: (\d+)')
    regex_base_lr = re.compile('base_lr: ([\.\deE+-]+)')
    regex_test_interval = re.compile('test_interval: (\d+)')
    regex_solver_mode = re.compile('solver_mode: ([A-Z]+)')	#GPU or CPU
    regex_iteration = re.compile('Iteration (\d+)')
    regex_train_output = re.compile('Train net output #(\d+): (\S+) = ([\.\deE+-]+)')
    regex_test_output = re.compile('Test net output #(\d+): (\S+) = ([\.\deE+-]+)')
    regex_learning_rate = re.compile('lr = ([-+]?[0-9]*\.?[0-9]+([eE]?[-+]?[0-9]+)?)')

    iteration = -1
    learning_rate = float('NaN')
    train_dict_list = []
    test_dict_list = []
    info_dict_list = []
    train_row = None
    test_row = None
    mode = "NaN"
    test_interval = -1
    base_lr = 0.0
    momentum = 0.0
    weight_decay = 0.0
    max_iter = -1
    lr_policy = "NaN"
    gamma = 0.0
    power = 0.0
    print_once = True

    with open(path_to_log) as f:
        for line in f:

       	    if print_once:
		tst_interval = regex_test_interval.search(line)
		if tst_interval:
		    test_interval = tst_interval.group(1)
		bs_lr = regex_base_lr.search(line)
		if bs_lr:
		    base_lr = bs_lr.group(1)
		momentm = regex_momentum.search(line)
		if momentm:
		    momentum = momentm.group(1)
		wgt_decay = regex_weight_decay.search(line)
		if wgt_decay:
		    weight_decay = wgt_decay.group(1)
     		mx_iter = regex_max_iter.search(line)
		if mx_iter:
		    max_iter = mx_iter.group(1)
		lr_poli = regex_lr_policy.search(line)
		if lr_poli:
		    lr_policy = lr_poli.group(1)
		gama = regex_gamma.search(line)
		if gama:
		    gamma = gama.group(1)
		pwr = regex_power.search(line)
		if pwr:
		    power = pwr.group(1)
		solver_mode = regex_solver_mode.search(line)
		if solver_mode:
		    mode = solver_mode.group(1)	
		    print_once = False
	    iteration_match = regex_iteration.search(line)
            if iteration_match:
                iteration = float(iteration_match.group(1))
            if iteration == -1:
                continue
            learning_rate_match = regex_learning_rate.search(line)
            if learning_rate_match:
                learning_rate = float(learning_rate_match.group(1))

            train_dict_list, train_row = Parse_Line_For_Output(
                regex_train_output, train_row, train_dict_list,
                line, iteration, learning_rate
            )
            test_dict_list, test_row = Parse_Line_For_Output(
                regex_test_output, test_row, test_dict_list,
                line, iteration, learning_rate
            )

    info_row = OrderedDict([
                ('test_interval', test_interval),
                ('base_lr', base_lr),
		('momentum', momentum),
		('weight_decay', weight_decay),
		('lr_policy', lr_policy),
		('gamma', gamma),
		('power', power),
		('max_iter', max_iter),
		('mode', mode)
            ])
    info_dict_list.append(info_row)
    Fix_Initial_None(train_dict_list, isTrain=True)
    Fix_Initial_None(test_dict_list, isTrain=False)
    return train_dict_list, test_dict_list, info_dict_list

def Write_Csv(output_filename, dict_list, delimiter):
    if not dict_list:
        return
    dialect = csv.excel
    dialect.delimiter = delimiter
    with open(output_filename, 'w') as f:
        dict_writer = csv.DictWriter(f, fieldnames=dict_list[0].keys(), dialect=dialect)
        dict_writer.writeheader()
        dict_writer.writerows(dict_list)

def Save_Csv_Files(logfile_path, output_dir, train_dict_list, test_dict_list, info_dict_list, delimiter=','):
    log_basename = os.path.basename(logfile_path)    
    train_filename = os.path.join(output_dir, log_basename + '.train')
    Write_Csv(train_filename, train_dict_list, delimiter)
    test_filename = os.path.join(output_dir, log_basename + '.test')
    Write_Csv(test_filename, test_dict_list, delimiter)
    info_filename = os.path.join(output_dir, log_basename + '.info')
    Write_Csv(info_filename, info_dict_list, delimiter)

def main():
    args = Parse_Args()
    train_dict_list, test_dict_list, info_dict_list = Parse_Log(args.logfile_path)
    Save_Csv_Files(args.logfile_path, args.output_dir, train_dict_list,test_dict_list, info_dict_list, delimiter=args.delimiter)

if __name__ == '__main__':
    main()

