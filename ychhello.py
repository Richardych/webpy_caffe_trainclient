from __future__ import (absolute_import, division, print_function, unicode_literals)
import web
import os
import sys
import pandas as pd
import subprocess
import json
from web import form
from rq import Connection, Queue
from fib import startcaffe, stopcaffe
from redis import Redis
#web.config.debug = False

urls = (
    '/', 'hello',
    '/track','track'
)

render = web.template.render('templates/')
class hello:  
    def GET(self):
   	command = 'python ' + '/home/deepglint/caffe/ych/' +'ych_gpu.py'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        gpuinfo = pd.read_csv('/home/deepglint/caffe/ych/'+'ychgpu.csv',delimiter=',')
        return render.index(gpuinfo)

    def POST(self):
        ts = web.input()['checktrain']
        with Connection():
	    if ts=="stop":
		q = Queue('high', connection=Redis(), default_timeout=5)
		q.enqueue(stopcaffe)
	    elif ts=="start":
                q = Queue('low', connection=Redis(), default_timeout=100)
                q.enqueue(startcaffe, web.input()['traincmd'])
        command = 'python ' + '/home/deepglint/caffe/ych/' +'ych_gpu.py'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        gpuinfo = pd.read_csv('/home/deepglint/caffe/ych/'+'ychgpu.csv',delimiter=',')
        return render.index(gpuinfo)

class track:

    def POST(self):
	command = 'python ' + web.input()['savepath'] + 'ych_parselog.py ' + web.input()['savepath'] \
	+web.input()['logfilename'] + ' ' + web.input()['savepath']
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	process.wait()
        caffeinfo = pd.read_csv(web.input()['savepath']+web.input()['logfilename'] + '.info', delimiter=',')
	command = 'python ' + web.input()['savepath'] + 'plot_learning_curve.py '+ web.input()['savepath'] \
	+web.input()['logfilename'] + ' /home/deepglint/mWeb/static/tmp.png ' + str(caffeinfo['max_iter'][0])
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        command = 'python ' + web.input()['savepath']+'ych_gpu.py'
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
	gpuinfo = pd.read_csv(web.input()['savepath']+'ychgpu.csv',delimiter=',')
 	return render.index1(caffeinfo,gpuinfo,web.input()['logfilename'],
			     web.input()['savepath'])
        #return web.data()  
        #raise web.seeother('/')

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()  








