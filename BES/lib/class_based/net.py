#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PythonPie <contact@pythonpie.com>
# Copyright (c) 2015 - THSTACK <contact@thstack.com>

""" pymonitor client module: ��ȡ�������ݣ���/proc/net/dev �ļ� """
""" @Site: www.pythonpie.com
    @Date: 2015-06-05
    @Version: v1.2
    @Note:
        ��Ҫһ�������ļ� /tmp/proc_net_dev ��������һ�ε�����
        ����һ����ʱ��������ݣ�
        ���μ����ʱ���ñ������ݺ���һ��������������ֵ,������ʱ����ļ�����
        ֵ������������ս��(kb/s)

        /proc/net/dev �����ݵĽ��ͣ�
            [root@ashinamo ~]# cat /proc/net/dev
            Inter-|   Receive                                                |  Transmit
             face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
                lo:664087762 3663780    0    0    0     0          0         0 664087762 3663780    0    0    0     0       0          0
              eth0:  651822    6311    0    0    0     0          0         0   553421    6076    0    0    0     0       0          0
              eth1:  663326    6060    0    0    0     0          0         0   962066    4571    0    0    0     0       0          0
            interface:������
            Receive(����):
                ��һ����(bytes)���ֽ���
                �ڶ�����(packets)������
                ��������(errs)���������
                ���ĸ���(drop)����������
                �������(fifo)��(First in first out)����/FIFO���������
                ��������(frame)��֡��
                ���߸���(compressed)��ѹ��(compressed)����
                �ڰ˸���(multicast)���ಥ��multicast, ����㲥�������鲥��)����
            Transmit(����):
                ��һ����(bytes)���ֽ���
                �ڶ�����(packets)������
                ��������(errs)���������
                ���ĸ���(drop)����������
                �������(fifo)��(First in first out)����/FIFO���������
                ��������(colls): �ӿڼ�⵽�ĳ�ͻ��
                ���߸���(carrier): ���ӽ��ʳ��ֹ��ϴ������磺���߽Ӵ�����
                �ڰ˸���(compressed)��ѹ��(compressed)����

"""

import re
import time
import simplejson as json


class NetData:
    def __init__(self, devices):
        self.now_data = {}
        self.last_data = {}
        self.devices = devices

    def get_now_data(self):
        """��ȡ���統ǰϵͳ����

        @Return: (status, msgs, results)
            status = INT, # Function execution status,
                            0 is normal, other is failure.
            msgs = STRING, # If status equal to 0, msgs is '',
                             otherwise will be filled with error message.
            result = DICT {
                'timestamp': 1432342587.661646, #��ȡ����ʱ��
                'eth0': {
                    # ����
                    'receive_bytes': '3196699', # �ֽ���
                    'receive_packets': '34412', # ����
                    'receive_errs': '0', # �������
                    'receive_drop': '0', # ��������
                    'receive_fifo': '0', # (First in first out)����/
                    FIFO���������
                    'receive_frame': '0', # ֡��
                    'receive_compressed': '0', # ѹ������
                    'receive_multicast': '0',  # �ಥ��multicast,
                    ����㲥�������鲥��)����

                    # ����
                    'transmit_bytes': '3635965', # �ֽ���
                    'transmit_packets': '18783', # ����
                    'transmit_errs': '0', # �������
                    'transmit_drop': '0', # ��������
                    'transmit_fifo': '0', # (First in first out)����/
                    FIFO���������
                    'transmit_colls': '0', # �ӿڼ�⵽�ĳ�ͻ��
                    'transmit_carrier': '0' # ���ӽ��ʳ��ֹ��ϴ���,
                    �磺���߽Ӵ�����
                    'transmit_compressed': '0', # ѹ��(compressed)����
                }

            }
        """
        try:
            results = file('/proc/net/dev').read()
        except:
            return (-1, 'system file not exist', '')

        self.now_data['timestamp'] = time.time()
        if not self.devices or type(self.devices) != list:
            return (-2, 'devices can not be none and must be a list', '')
        for device in self.devices:
            pat = device + ":.*"
            try:
                devicedata = re.search(pat, results).group()
            except:
                return (-2, device+' not exist', '')

            tmp_main = devicedata.split(":")
            tmp = tmp_main[1].split()
            self.now_data[tmp_main[0].strip()] = {
                'receive_bytes': tmp[0],
                'receive_packets': tmp[1],
                'receive_errs': tmp[2],
                'receive_drop': tmp[3],
                'receive_fifo': tmp[4],
                'receive_frame': tmp[5],
                'receive_compressed': tmp[6],
                'receive_multicast': tmp[7],
                'transmit_bytes': tmp[8],
                'transmit_packets': tmp[9],
                'transmit_errs': tmp[10],
                'transmit_drop': tmp[11],
                'transmit_fifo': tmp[12],
                'transmit_colls': tmp[13],
                'transmit_carrier': tmp[14],
                'transmit_compressed': tmp[15]
            }
            return (0, '', self.now_data)

    def get_last_data(self):
        """��ȡ��һʱ������ϵͳ����

        @Return: (status, msgs, results)
            status = INT, # Function execution status,
                            0 is normal, other is failure.
            msgs = STRING, # If status equal to 0, msgs is '',
                             otherwise will be filled with error message.
            result = DICT {
                'timestamp': 1432342587.661646, #��ȡ����ʱ��
                'eth0': {
                    # ����
                    'receive_bytes': '3196699', # �ֽ���
                    'receive_packets': '34412', # ����
                    'receive_errs': '0', # �������
                    'receive_drop': '0', # ��������
                    'receive_fifo': '0', # (First in first out)����/
                    FIFO���������
                    'receive_frame': '0', # ֡��
                    'receive_compressed': '0', # ѹ������
                    'receive_multicast': '0',  # �ಥ��multicast,
                    ����㲥�������鲥��)����

                    # ����
                    'transmit_bytes': '3635965', # �ֽ���
                    'transmit_packets': '18783', # ����
                    'transmit_errs': '0', # �������
                    'transmit_drop': '0', # ��������
                    'transmit_fifo': '0', # (First in first out)����/
                    FIFO���������
                    'transmit_colls': '0', # �ӿڼ�⵽�ĳ�ͻ��
                    'transmit_carrier': '0' # ���ӽ��ʳ��ֹ��ϴ�����
                    �磺���߽Ӵ�����
                    'transmit_compressed': '0', # ѹ��(compressed)����
                }

            }
        """
        # ��ȡ��ʷ����
        try:
            results = file('/tmp/proc_net_dev').read()
            self.last_data = json.loads("%s" % results.strip())
        except:
            self.last_data = self.now_data

        # д��ǰ���ݵ��ļ�
        fp = file('/tmp/proc_net_dev', 'w')
        fp.write(json.dumps(self.now_data))
        fp.close()
        return (0, '', self.last_data)

    def compute_data(self):
        """����ʱ�����ݣ��������紫������
        @Return: (status, msgs, results)
                status = INT, # Function execution status,
                                0 is normal, other is failure.
                msgs = STRING, # If status equal to 0, msgs is '',
                                 otherwise will be filled with error message.
                results = DICT {
                    'eth0': {  #����eth0�Ĵ�������
                        'receive': 0, #��λ������˵������ KB/s
                        'transmit': 0
                    }
                }
        """
        now_status, now_msgs, now_data = self.get_now_data()
        last_status, last_msgs, last_data = self.get_last_data()
        if now_status == last_status == 0:
            # �����������ݣ��õ�Ҫ�����ֵ
            results = {}
            timecut = \
                float(now_data['timestamp']) - float(last_data['timestamp'])
            if timecut > 0:
                for key in self.devices:
                    now_data_rece = int(now_data[key]['receive_bytes'])
                    last_data_rece = int(last_data[key]['receive_bytes'])
                    now_data_trans = int(now_data[key]['transmit_bytes'])
                    last_data_trans = int(last_data[key]['transmit_bytes'])
                    receive = \
                        (now_data_rece - last_data_rece) / float(1024)/timecut
                    transmit = \
                        (now_data_trans - last_data_trans) / float(1024)/timecut
                    results[key] = \
                        {'receive': int(receive), 'transmit': int(transmit)}
            else:
                # ��һ�μ��ص�ʱ����ʷ����Ϊ�գ��޷����㣬���Գ�ʼ��Ϊ0
                for key in self.devices:
                    results[key] = {'receive': 0, 'transmit': 0}
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
    netdata = NetData(['eth0'])
    netdata.run()
