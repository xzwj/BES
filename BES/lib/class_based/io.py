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

import re
import time
import simplejson as json


class IoData:
    def __init__(self, devices):
        self.now_data = {}
        self.last_data = {}
        self.devices = devices

    def get_now_data(self):
        """��ȡio��ǰϵͳ����

        @Return: (status, msgs, results)
            status = INT, # Function execution status,
                            0 is normal, other is failure.
            msgs = STRING, # If status equal to 0, msgs is '',
                             otherwise will be filled with error message.
            result = DICT {
                'timestamp': 1432320942.659233, # ���ݻ�ȡʱ��
                'sda': {  # ����
                    'number_of_issued_reads': '54579', # �����̵Ĵ���,
                    �ɹ���ɶ����ܴ���
                    'number_of_reads_merged': '39', # �ϲ�������
                    'number_of_sectors_read': '811574', #  �������Ĵ�����
                    �ɹ������������ܴ���
                    'number_of_milliseconds_spent_reading': '17188',
                    # �����ѵĺ��������������ж����������ѵĺ�����
                    'number_of_writes_completed': '4441',
                    # д��ɵĴ������ɹ�д��ɵ��ܴ���
                    number_of_writes_merged': '6155', # �ϲ�д������
                    Ϊ��Ч�ʿ��ܻ�ϲ����ڵĶ���д��
                    �Ӷ�����4K�Ķ��������ձ�����������֮ǰ���ܻ���
                    һ��8K�Ķ����ű����������Ŷӣ������ֻ��һ��I/O������
                    �����ʹ��֪�������Ĳ����ж�Ƶ��
                    'number_of_sectors_written': '146072',  # д�����Ĵ�����
                    �ɹ�д�����ܴ���
                    'number_of_milliseconds_spent_writing': '3388',
                    # д���ѵĺ���������������д���������ѵĺ�����
                    'number_of_IOs_currently_in_progress': '0',
                    # I/O�ĵ�ǰ���ȣ�ֻ�������Ӧ����0��
                    �����󱻽����ʵ���request_queue_tʱ���Ӻ��������ʱ��С
                    'number_of_milliseconds_spent_doing_IOs': '14876',
                    # ����I/O�����ϵĺ�����������������ֻҪfield 9��Ϊ0
                    'number_of_milliseconds_spent_doing_IOs_2': '20508'
                    # ��Ȩ������I/O�����ϵĺ���������ÿ��I/O��ʼ��I/O������
                    I/O�ϲ�ʱ����򶼻����ӡ�����Ը�I/O���ʱ��ʹ洢��Щ
                    �����ۻ����ṩһ�������Ĳ�����׼
                }
            }
        """
        # ��ȡ��ǰ����
        try:
            fp = file('/proc/diskstats')
            raw_data = fp.read()
            fp.close()
        except:
            return (-2, 'system file not exist', '')

        self.now_data['timestamp'] = time.time()
        if not self.devices or type(self.devices) != list:
            return (-2, 'devices can not be none and must be a list', '')
        try:
            for device in self.devices:
                pat = device + " .*"
                try:
                    devicedata = re.search(pat, raw_data).group()
                except:
                    return (-3, device + ' not exist', '')
                tmp = devicedata.split()
                self.now_data[tmp[0]] = {
                    'number_of_issued_reads': tmp[1],  # Field 1
                    'number_of_reads_merged': tmp[2],  # Field 2
                    'number_of_sectors_read': tmp[3],  # Field 3
                    'number_of_milliseconds_spent_reading': tmp[4],  # Field 4
                    'number_of_writes_completed': tmp[5],  # Field 5
                    'number_of_writes_merged': tmp[6],  # Field 6
                    'number_of_sectors_written': tmp[7],  # Field 7
                    'number_of_milliseconds_spent_writing': tmp[8],  # Field 8
                    'number_of_IOs_currently_in_progress': tmp[9],  # Field 9
                    'number_of_milliseconds_spent_doing_IOs': tmp[10],
                    # Field10
                    'number_of_milliseconds_spent_doing_IOs_2': tmp[11],
                    # Field 11
                }
            return (0, '', self.now_data)
        except:
            return (-2, 'system data format is error', '')

    def get_last_data(self):
        """��ȡio��һʱ��ϵͳ����

        @Return: (status, msgs, results)
            status = INT, # Function execution status,
                            0 is normal, other is failure.
            msgs = STRING, # If status equal to 0, msgs is '',
                             otherwise will be filled with error message.
            result = DICT {
                'timestamp': 1432320942.659233, # ���ݻ�ȡʱ��
                'sda': {  # ����
                    'number_of_issued_reads': '54579', # �����̵Ĵ�����
                    �ɹ���ɶ����ܴ���
                    'number_of_reads_merged': '39', # �ϲ�������
                    'number_of_sectors_read': '811574', #  �������Ĵ�����
                    �ɹ������������ܴ���
                    'number_of_milliseconds_spent_reading': '17188',
                    # �����ѵĺ��������������ж����������ѵĺ�����
                    'number_of_writes_completed': '4441',  # д��ɵĴ�����
                    �ɹ�д��ɵ��ܴ���
                    number_of_writes_merged': '6155', # �ϲ�д������
                    Ϊ��Ч�ʿ��ܻ�ϲ����ڵĶ���д���Ӷ�����4K�Ķ��������ձ�
                    ����������֮ǰ���ܻ���һ��8K�Ķ����ű����������Ŷӣ���
                    ���ֻ��һ��I/O�����������ʹ��֪�������Ĳ����ж�Ƶ��
                    'number_of_sectors_written': '146072',  # д�����Ĵ�����
                    �ɹ�д�����ܴ���
                    'number_of_milliseconds_spent_writing': '3388', # д���ѵ�
                    ����������������д���������ѵĺ�����
                    'number_of_IOs_currently_in_progress': '0',  # I/O�ĵ�ǰ
                    ���ȣ�ֻ�������Ӧ����0�������󱻽����ʵ���
                    request_queue_tʱ���Ӻ��������ʱ��С
                    'number_of_milliseconds_spent_doing_IOs': '14876', # ����
                    I/O�����ϵĺ�����������������ֻҪfield 9��Ϊ0
                    'number_of_milliseconds_spent_doing_IOs_2': '20508' # ��
                    Ȩ������I/O�����ϵĺ���������ÿ��I/O��ʼ��I/O������I/O��
                    ��ʱ����򶼻����ӡ�����Ը�I/O���ʱ��ʹ洢��Щ������
                    �����ṩһ�������Ĳ�����׼
                }
            }
        """
        # ��ȡ��ʷ����
        try:
            fp = file('/tmp/proc_diskstats')
            results = fp.read()
            fp.close()
            self.last_data = json.loads("%s" % results.strip())
        except:
            self.last_data = self.now_data
        # ���浱ǰ���ݵ���ʷ���ݱ���
        fp = file('/tmp/proc_diskstats', 'w')
        fp.write(json.dumps(self.now_data))
        fp.close()
        return (0, '', self.last_data)

    def compute_data(self):
        """����ʱ�����ݣ�����cpu��ռ����

        @Return: (status, msgs, results)
                status = INT, # Function execution status,
                                0 is normal, other is failure.
                msgs = STRING, # If status equal to 0, msgs is '',
                                 otherwise will be filled with error message.
                results = DICT {
                    'sda':{  # ����
                        'reading': 0, # �� ��λ�� KB/s
                        'writing': 0  # д ��λ�� KB/s
                    }
                }
        """

        now_status, now_msgs, now_data = self.get_now_data()
        last_status, last_msgs, last_data = self.get_last_data()
        if now_status == last_status == 0:

            # �����������ݣ��õ�Ҫ�����ֵ
            results = {}
            timecut = float(now_data['timestamp']) - \
                float(last_data['timestamp'])
            if timecut > 0:
                for key in self.devices:
                    now_data_read = \
                        int(now_data[key]['number_of_sectors_read'])
                    last_data_read = \
                        int(last_data[key]['number_of_sectors_read'])
                    now_data_write = \
                        int(now_data[key]['number_of_sectors_written'])
                    last_data_write = \
                        int(last_data[key]['number_of_sectors_written'])
                    reading = \
                        (now_data_read - last_data_read) / float(2) / timecut
                    writing = \
                        (now_data_write - last_data_write) / float(2) / timecut
                    results[key] = \
                        {'reading': int(reading), 'writing': int(writing)}
            else:
                # ��һ�μ��ص�ʱ����ʷ����Ϊ��, �޷����㣬���Գ�ʼ��Ϊ0
                for key in self.devices:
                    results[key] = {'reading': 0, 'writing': 0}
            return (0, '', results)
        elif now_status != 0:
            return (now_status, now_msgs, now_data)
        else:
            return (last_status, last_msgs, last_data)

    def run(self):
        """������ȡio����
        @Return: None
        """
        while True:
            result = self.compute_data()
            if result[0] == 0:
                print result
            else:
                print result
                break
            time.sleep(1)


if __name__ == "__main__":
    iodata = IoData(['sda'])
    iodata.run()
