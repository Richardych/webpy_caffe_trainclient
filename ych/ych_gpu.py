import numpy as np
import pandas as pd
import pynvml as pn
from pynvml import *
import csv
from collections import OrderedDict

def Start():
    try:
        pn.nvmlInit()
    except pn.NVMLError, err:
        print "Failed to initialize NVML: ", err
        print "Exiting..."
        os._exit(1)

def Shutdown():
    try:
        pn.nvmlShutdown()
    except pn.NVMLError, err:
        print "Error shutting down NVML:"

def Get_Devicecount():
    return int(pn.nvmlDeviceGetCount())

def Get_GpuInfo(deviceCount):
    gpu_dict = {}
    tmp_dict = {}
    for i in range(0, deviceCount):
	tmp_dict = {}
        handle = pn.nvmlDeviceGetHandleByIndex(i)
        pciInfo = pn.nvmlDeviceGetPciInfo(handle)
        gpu_id= pciInfo.busId
        product_name=pn.nvmlDeviceGetName(handle)
        try:
	    mode=pn.nvmlDeviceGetPersistenceMode(handle)  #0:Disable
        except pn.NVMLError, err:
	    mode='NA'
        try:
	    Current_driver_model = pn.nvmlDeviceGetCurrentDriverModel(handle)
 	except pn.NVMLError, err:
	    Current_driver_model='NA'
 	try:
	    uuid=pn.nvmlDeviceGetUUID(handle)
        except np.NVMLError, err:
	    uuid='NA'
	pci_device_id=pciInfo.pciDeviceId
        pci_bus_id=pciInfo.busId
	try:
            width=pn.nvmlDeviceGetMaxPcieLinkWidth(handle)
	except np.NVMLError, err:
	    width='NA'
	try:
            memInfo = pn.nvmlDeviceGetMemoryInfo(handle)
            mem_total = str(memInfo.total / 1024 / 1024) + ' MB'
            mem_used = str(memInfo.used / 1024 / 1024) + ' MB'
            mem_free = str(memInfo.free / 1024 / 1024) + ' MB'
	except np.NVMLError, err:
	    mem_total = 'NA'
            mem_used = 'NA'
            mem_free = 'NA'

        try:
            util = nvmlDeviceGetUtilizationRates(handle)
            gpu_util = str(util.gpu)
            mem_util = str(util.memory)
        except pn.NVMLError, err:
	    gpu_util = 'NA'
	    mem_util = 'NA'            
        try:
            temp = pn.nvmlDeviceGetTemperature(handle, pn.NVML_TEMPERATURE_GPU)
        except np.NVMLError, err:
	    temp = 'NA'
	try:
            powMan = pn.nvmlDeviceGetPowerManagementMode(handle)
        except pn.NVMLError, err:
            powMan = 'NA'
        try:
            graphics_clock = pn.nvmlDeviceGetClockInfo(handle, pn.NVML_CLOCK_GRAPHICS)
        except pn.NVMLError, err:
            graphics_clock = 'NA'
	try:
            mem_clock = pn.nvmlDeviceGetClockInfo(handle, pn.NVML_CLOCK_MEM)
        except np.NVMLError, err:
	    mem_clock = 'NA'
	try:
	    perf_stat = pn.nvmlDeviceGetPowerState(handle)
	except np.NVMLError, err:
	    perf_stat = 'NA'
	tmp_dict['Gpu_Id'] = gpu_id
	tmp_dict['Product_Name'] = product_name
	tmp_dict['Mode'] = mode
	tmp_dict['Current_Driver_Model'] = Current_driver_model
	tmp_dict['Total_Memory'] = mem_total
	tmp_dict['Used_Memory'] = mem_used
	tmp_dict['Free_Memory'] = mem_free
	tmp_dict['GPU_Util'] = gpu_util+'%'
	tmp_dict['Memory_Util'] = mem_util+'%'
	tmp_dict['Temperature'] = str(temp)+'C'
	tmp_dict['Graphics_Clock'] = graphics_clock
	tmp_dict['Memory_Clock'] = mem_clock
	tmp_dict['Perf_State'] = perf_stat
	gpu_dict[i] = tmp_dict
	return gpu_dict

Start()

FIELDS = ['Gpu_Id','Product_Name','Mode','Current_Driver_Model','Total_Memory','Used_Memory','Free_Memory','GPU_Util','Memory_Util','Temperature','Graphics_Clock','Memory_Clock','Perf_State']
deviceCount = Get_Devicecount()
gpudict = Get_GpuInfo(deviceCount)

csv_file = open('/home/deepglint/caffe/ych/ychgpu.csv', 'wb')  
writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
writer.writerow(dict(zip(FIELDS, FIELDS)))
for x in range(len(gpudict)):
    writer.writerow(gpudict[x])  
csv_file.close()

Shutdown()


