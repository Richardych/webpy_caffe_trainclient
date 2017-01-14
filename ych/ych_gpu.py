import numpy as np
import pandas as pd
import pynvml as pn
from pynvml import *
import csv
from collections import OrderedDict

def Start():
    try:
        pn.nvmlInit()    #初始化NVML
    except pn.NVMLError, err:
        print "Failed to initialize NVML: ", err
        print "Exiting..."
        os._exit(1)

def Shutdown():
    try:
        pn.nvmlShutdown()    #关闭NVML
    except pn.NVMLError, err:
        print "Error shutting down NVML:"

def Get_Devicecount():
    return int(pn.nvmlDeviceGetCount())    #获得可用GPU数量

def Get_GpuInfo(deviceCount):
    gpu_dict = {}
    tmp_dict = {}
    for i in range(0, deviceCount):
	tmp_dict = {}
        handle = pn.nvmlDeviceGetHandleByIndex(i)    #获得某一个ID 的gpu句柄
        pciInfo = pn.nvmlDeviceGetPciInfo(handle)    #检索此设备的PCI属性
        gpu_id= pciInfo.busId
        product_name=pn.nvmlDeviceGetName(handle)    #检索此设备名称
        try:
	    mode=pn.nvmlDeviceGetPersistenceMode(handle)  #检索与此设备关联的持久性模式,0:Disable
        except pn.NVMLError, err:
	    mode='NA'
        try:
	    Current_driver_model = pn.nvmlDeviceGetCurrentDriverModel(handle)    #检索当前驱动模式
 	except pn.NVMLError, err:
	    Current_driver_model='NA'
 	try:
	    uuid=pn.nvmlDeviceGetUUID(handle)    #检索与此设备相关联的全局唯一不可变UUID
        except np.NVMLError, err:
	    uuid='NA'
	pci_device_id=pciInfo.pciDeviceId    #检索该gpu的pci设备id
        pci_bus_id=pciInfo.busId             #总线id
	try:
            width=pn.nvmlDeviceGetMaxPcieLinkWidth(handle)    #检索此设备和系统可能的最大PCIe链路宽度
	except np.NVMLError, err:
	    width='NA'
	try:
            memInfo = pn.nvmlDeviceGetMemoryInfo(handle)    #检索设备上已用空间，可用空间和总内存量
            mem_total = str(memInfo.total / 1024 / 1024) + ' MB'
            mem_used = str(memInfo.used / 1024 / 1024) + ' MB'
            mem_free = str(memInfo.free / 1024 / 1024) + ' MB'
	except np.NVMLError, err:
	    mem_total = 'NA'
            mem_used = 'NA'
            mem_free = 'NA'

        try:
            util = nvmlDeviceGetUtilizationRates(handle)    #检索设备主要子系统的当前利用率
            gpu_util = str(util.gpu)    #gpu利用率
            mem_util = str(util.memory)    #显存利用率
        except pn.NVMLError, err:
	    gpu_util = 'NA'
	    mem_util = 'NA'            
        try:
            temp = pn.nvmlDeviceGetTemperature(handle, pn.NVML_TEMPERATURE_GPU)    #获取GPU当前温度
        except np.NVMLError, err:
	    temp = 'NA'
	try:
            powMan = pn.nvmlDeviceGetPowerManagementMode(handle)    #获取设备当前的电源管理模式
        except pn.NVMLError, err:
            powMan = 'NA'
        try:
            graphics_clock = pn.nvmlDeviceGetClockInfo(handle, pn.NVML_CLOCK_GRAPHICS)    #检索设备的当前时钟速度
        except pn.NVMLError, err:
            graphics_clock = 'NA'
	try:
            mem_clock = pn.nvmlDeviceGetClockInfo(handle, pn.NVML_CLOCK_MEM)
        except np.NVMLError, err:
	    mem_clock = 'NA'
	try:
	    perf_stat = pn.nvmlDeviceGetPowerState(handle)    #检索设备的当前性能状
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


