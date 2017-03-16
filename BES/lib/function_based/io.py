#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PythonPie <contact@pythonpie.com>
# Copyright (c) 2015 - THSTACK <contact@thstack.com>

""" ��ȡIO���ݣ� ��/proc/diststats �ļ� """
""" @Site: www.pythonpie.com
    @Date: 2015-05-23
    @Version: v1.2
    @Note:
        ��Ҫһ�������ļ� /tmp/last_diskstats ��������һ�ε�����
        (��һ����ʱ���������)
        ���μ����ʱ�� �ñ������ݺ���һ��������������ֵ,
        ������ʱ����ļ�����ֵ ������������ս��

        /proc/disktats �е������ݵĽ��ͣ�

            [root@ashinamo ~]# cat /proc/diskstats | grep sda
               8       0 sda 3479 5666 288738 199185 496 957 11624 11944 0 19732 211125
            ��1���򣺶����̵Ĵ������ɹ���ɶ����ܴ�����
            ��2���򣺺ϲ���������
            ��3���򣺶������Ĵ������ɹ������������ܴ�����
            ��4���򣺶����ѵĺ��������������ж����������ѵĺ�������//��׼
            ��5����д��ɵĴ������ɹ�д��ɵ��ܴ�����
            ��6���򣺺ϲ�д������Ϊ��Ч�ʿ��ܻ�ϲ����ڵĶ���д��
                     �Ӷ�����4K�Ķ��������ձ�����������֮ǰ���ܻ�
                     ���һ��8K�Ķ����ű����������Ŷӣ���
                     ���ֻ��һ��I/O�����������ʹ��֪�������Ĳ����ж�Ƶ����
            ��7����д�����Ĵ������ɹ�д�����ܴ�����
            ��8����д���ѵĺ���������������д���������ѵĺ�������//��׼
            ��9����I/O�ĵ�ǰ���ȣ�ֻ�������Ӧ����0��
                     �����󱻽����ʵ���request_queue_tʱ���Ӻ��������ʱ��С��
            ��10���򣺻���I/O�����ϵĺ�����������������ֻҪfield 9��Ϊ0��
            ��11���򣺼�Ȩ������I/O�����ϵĺ���������ÿ��I/O��ʼ��I/O������
                      I/O�ϲ�ʱ����򶼻����ӡ�����Ը�I/O���ʱ��ʹ洢
                      ��Щ�����ۻ����ṩһ�������Ĳ�����׼��

"""

import simplejson as json
import time
import re


def get_ProcDiskstats(devices):
    """ ��ȡIO�������
        @Params: devices = LIST # ����Ӳ�̵��豸��,
                 ���� devices=['sda', 'sdb', 'hda', 'scisi']
        @Return: (status, msgs, results)
                status = INT, # Fuction execution status,
                                0 is normal, other is failure.
                msgs = STRING, # If status equal to 0, msgs is '',
                                 otherwise will be filled with error message.
                results = DICT {
                    'sda': { # �豸sda�Ķ�д����
                        'reading': 50032, # ��λ����  KB/s
                        'writing': 20,
                    },
                    'sdb': {
                        'reading': 50032, # ��λ����  KB/s
                        'writing': 20,
                    }
                }

        @Note:
            ��ȡ���ݵ�Ч���� �� #vmstat -n 1 һ��
    """

    status = 0
    msgs = ''
    results = ''
    if devices == []:
        return (-1, 'Error: Params is None.', '')

    now_data = {}  # ��ǰ /proc/diskstats  ��ֵ
    last_data = {}  # ��һ�� /proc/diskstats  ��ֵ, ʱ�����ɵ��ó������

    # ��ȡ��ǰ����
    try:
        fp_o = file('/proc/diskstats')
        raw_data = fp_o.read()
        fp_o.close()
    except:
        return (-2, 'system file not exist', '')

    now_data['timestamp'] = time.time()
    try:
        for device in devices:
            pat = device + " .*"
            try:
                devicedata = re.search(pat, raw_data).group()
            except:
                return (-3, device + ' not exist', '')
            tmp = devicedata.split()
            now_data[tmp[0]] = {
                'number_of_issued_reads': tmp[1],  # Field 1
                'number_of_reads_merged': tmp[2],  # Field 2
                'number_of_sectors_read': tmp[3],  # Field 3
                'number_of_milliseconds_spent_reading': tmp[4],  # Field 4
                'number_of_writes_completed': tmp[5],      # Field 5
                'number_of_writes_merged': tmp[6],         # Field 6
                'number_of_sectors_written': tmp[7],       # Field 7
                'number_of_milliseconds_spent_writing': tmp[8],    # Field 8
                'number_of_IOs_currently_in_progress': tmp[9],    # Field 9
                'number_of_milliseconds_spent_doing_IOs': tmp[10],   # Field 10
                'number_of_milliseconds_spent_doing_IOs_2': tmp[11],  # Field11
            }
    except:
        return (-2, 'system data format is error', '')

    # ��ȡ��ʷ����
    try:
        file_o = file('/tmp/proc_diskstats')
        results = file_o.read()
        file_o.close()
        last_data = json.loads("%s" % results.strip())
    except:
        last_data = now_data

    # ���浱ǰ���ݵ���ʷ���ݱ���
    fp = file('/tmp/proc_diskstats', 'w')
    fp.write(json.dumps(now_data))
    fp.close()

    # �����������ݣ��õ�Ҫ�����ֵ
    results = {}
    timecut = float(now_data['timestamp']) - float(last_data['timestamp'])
    if timecut > 0:
        for key in devices:
            now_data_read = int(now_data[key]['number_of_sectors_read'])
            last_data_read = int(last_data[key]['number_of_sectors_read'])
            now_data_write = int(now_data[key]['number_of_sectors_written'])
            last_data_write = int(last_data[key]['number_of_sectors_written'])
            reading = (now_data_read - last_data_read) / float(2) / timecut
            writing = (now_data_write - last_data_write) / float(2) / timecut
            results[key] = {'reading': int(reading), 'writing': int(writing)}
    else:
        # ��һ�μ��ص�ʱ����ʷ����Ϊ��, �޷����㣬���Գ�ʼ��Ϊ0
        for key in devices:
            results[key] = {'reading': 0, 'writing': 0}
    return (status, msgs, results)

if __name__ == "__main__":
    while True:
        print get_ProcDiskstats(devices=['sda', ])
        time.sleep(1)
