#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PythonPie <contact@pythonpie.com>
# Copyright (c) 2015 - THSTACK <contact@thstack.com>

""" ��ȡcpu���ݣ� �� /proc/stat �ļ� """
""" @Site: www.pythonpie.com
    @Date: 2015-05-23
    @Version: v1.2
    @Note:
        ��Ҫһ�������ļ� /tmp/proc_stat ��������һ�ε����ݡ�
        ���μ����ʱ�򣬣��ñ�������total���ϴ�total���� - ��������idle��
        �ϴ�idle����/��������total���ϴ�total���*100,
        ��Ȼ���������㹻�̵�ʱ������

        /proc/stat ��������ݽ��ͣ�
            [root@ashinamo sbin]# cat /proc/stat| grep cpu
            cpu  182835 0 64263 2012611 14849 244 20165 0 0

            ��λ(jiffies)��(jiffies���ں��е�һ��ȫ�ֱ�����
                            ������¼��ϵͳ����һ�������Ľ���������linux�У�
                            һ�����Ĵ��¿����Ϊ����ϵͳ���̵��ȵ���Сʱ��Ƭ��
                            ��ͬlinux�ں˿���ֵ�в�ͬ��ͨ����1ms��10ms֮��)

            ��һ����user (182835)    ��ϵͳ������ʼ�ۼƵ���ǰʱ�̣�
                                       �����û�̬������ʱ�䣬
                                       ������ niceֵΪ�����̡�
            �ڶ�����nice (0)         ��ϵͳ������ʼ�ۼƵ���ǰʱ�̣�
                                       niceֵΪ���Ľ�����ռ�õ�CPUʱ��

            ��������system (64263)   ��ϵͳ������ʼ�ۼƵ���ǰʱ�̣�
                                       ���ں���̬������ʱ��

            ���ĸ���idle (2012611)   ��ϵͳ������ʼ�ۼƵ���ǰʱ�̣�
                                       ��IO�ȴ�ʱ������������ȴ�ʱ��

            �������iowait (14849)   ��ϵͳ������ʼ�ۼƵ���ǰʱ�̣�
                                       IO�ȴ�ʱ��(since 2.5.41)

            ��������irq (244)        ��ϵͳ������ʼ�ۼƵ���ǰʱ�̣�
                                       Ӳ�ж�ʱ��(since 2.6.0-test4)

            ���߸���softirq (20165)  ��ϵͳ������ʼ�ۼƵ���ǰʱ�̣�
                                       ���ж�ʱ��(since 2.6.0-test4)

            �ڰ˸���stealstolen(0)   which is the time spent in other 
                                       operating systems when running in a 
                                       virtualized environment(since 2.6.11)

            �ھŸ���guest(0)         which is the time spent running 
                                       a virtual  CPU  for guest operating 
                                       systems under the control of the 
                                       Linux kernel(since 2.6.24)

"""

import time
import simplejson as json


class CpuData:
    def __init__(self):
        self.now_data = {}
        self.last_data = {}

    def get_now_data(self):
        """��ȡcpu��ǰϵͳ����

        @Return: (status, msgs, results)
            status = INT, # Function execution status,
                            0 is normal, other is failure.
            msgs = STRING, # If status equal to 0, msgs is '',
                             otherwise will be filled with error message.
            results = DICT {
                "idle": 749252, # ��ϵͳ������ʼ�ۼƵ���ǰʱ�̣�
                                  ��IO�ȴ�ʱ������������ȴ�ʱ��
                "total": 755982, # �ܵ� cpu ʱ��
                                   totalCpuTime = user + nice + system + 
                                                  idle + iowait + irq + 
                                                  softirq + stealstolen + guest
            }
        """
        # ��ȡ��ǰ����
        try:
            raw_data = file('/proc/stat').readlines()
        except:
            return (-1, 'system file not exist', '')

        results = raw_data[0].strip()
        cpu_all = results.split()
        cpu_all.pop(0)
        cpu_data = [int(i) for i in cpu_all]
        self.now_data['idle'] = cpu_data[3]
        self.now_data['total'] = sum(cpu_data)
        return (0, '', self.now_data)

    def get_last_data(self):
        """��ȡcpu�ϴε���ϵͳ����

        @Return: (status, msgs, results)
            status = INT, # Function execution status,
                            0 is normal, other is failure.
            msgs = STRING, # If status equal to 0, msgs is '',
                             otherwise will be filled with error message.
            results = DICT {
                "idle": 749252, # ��ϵͳ������ʼ�ۼƵ���ǰʱ�̣�
                                  ��IO�ȴ�ʱ������������ȴ�ʱ��
                "total": 755982, # �ܵ� cpu ʱ��
                                   totalCpuTime = user + nice + system + 
                                                  idle + iowait + irq + 
                                                  softirq + stealstolen + guest
            }
        """
        # ��ȡ��ʷ����
        try:
            raw_data = file('/tmp/proc_stat').read()
            self.last_data = json.loads("%s" % raw_data.strip())
        except:
            self.last_data = self.now_data

        # ���浱ǰ���ݵ���ʷ���ݱ���
        fp = file('/tmp/proc_stat', 'w')
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
                    "cpuuse": '34', #�ٷֱ�
                }
        """
        now_status, now_msgs, now_data = self.get_now_data()
        last_status, last_msgs, last_data = self.get_last_data()
        if now_status == last_status == 0:
            # �����������ݣ��õ�Ҫ�����ֵ
            results = {}
            diff_total = int(now_data['total']) - int(last_data['total'])
            diff_idle = (int(now_data['idle']) - int(last_data['idle']))
            if diff_total > 0:
                real_data = 100 * (float(diff_total - diff_idle) / diff_total)
                results['cpuuse'] = int(round(real_data))
            else:
                # ��һ�μ��ص�ʱ����ʷ����Ϊ�գ��޷����㣬 ���г�ʼ��Ϊ0
                results['cpuuse'] = 0
            return (0, '', results)
        elif now_status != 0:
            return (now_status, now_msgs, now_data)
        else:
            return (last_status, last_msgs, last_data)

    def run(self):
        """������ȡcpu����
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
    cpudata = CpuData()
    cpudata.run()
