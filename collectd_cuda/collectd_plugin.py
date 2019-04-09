#!/usr/bin/env python

import collectd
import subprocess
import numbers
import xml.etree.ElementTree as ET


def configure(conf):
        collectd.info('Configured with')

# Checks for N/A or ERR! readings and returns 0.0
def isvalid(reading):
        if reading == "N/A" or reading == "ERR!":
                return 0.0
        else:
                return float(reading)

def read(data=None):
        vl = collectd.Values(type='gauge')
        vl.plugin = 'cuda'

        out = subprocess.Popen(['nvidia-smi', '-q', '-x'], stdout=subprocess.PIPE).communicate()[0]
        root = ET.fromstring(out)

        # Changed root.iter() to root.getiterator() for Python 2.6 compatibility

        for gpu in root.getiterator('gpu'):
                # GPU id
                vl.plugin_instance = 'gpu-%s' % (gpu.find('minor_number').text)

                # GPU utilization
                vl.dispatch(type='percent', type_instance='gpu_util',
                            values=[isvalid(gpu.find('utilization/gpu_util').text.split()[0])])
                # GPU temperature
                vl.dispatch(type='temperature',
                            values=[isvalid(gpu.find('temperature/gpu_temp').text.split()[0])])
                # GPU power draw
                vl.dispatch(type='power', type_instance='power_draw',
                            values=[isvalid(gpu.find('power_readings/power_draw').text.split()[0])])
                # GPU memory utilization
                vl.dispatch(type='percent', type_instance='mem_util',
                            values=[isvalid(gpu.find('utilization/memory_util').text.split()[0])])
                # GPU encoder utilization
                vl.dispatch(type='percent', type_instance='enc_util',
                            values=[isvalid(gpu.find('utilization/encoder_util').text.split()[0])])
                # GPU decoder utilization
                vl.dispatch(type='percent', type_instance='dec_util',
                            values=[isvalid(gpu.find('utilization/decoder_util').text.split()[0])])
                # GPU memory usage
                vl.dispatch(type='memory', type_instance='used',
                            values=[1e6 * isvalid(gpu.find('fb_memory_usage/used').text.split()[0])])
                # GPU total memory
                vl.dispatch(type='memory', type_instance='total',
                            values=[1e6 * isvalid(gpu.find('fb_memory_usage/total').text.split()[0])])
                # GPU frequency
                vl.dispatch(type='cpufreq', type_instance='gpu_clock',
                            values=[1e6 * isvalid(gpu.find('clocks/graphics_clock').text.split()[0])])
                # GPU memory frequency
                vl.dispatch(type='cpufreq', type_instance='mem_clock',
                            values=[1e6 * isvalid(gpu.find('clocks/mem_clock').text.split()[0])])

collectd.register_config(configure)
collectd.register_read(read)
