# coding=gbk
from random import choice
import time
import csv
import os
import io
import sys
import random
import json
from urllib.request import urlopen
import urllib
from CommonUtil import CommonUtil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # �ı��׼�����Ĭ�ϱ���

util = CommonUtil()

Key = "0f1c4dd0c9d1be0d0b22d0581f60f17a"
lonRange = [116.2, 116.55]
latRange = [39.829652, 40.026057]
poi_hash = {
    "01": "����վ",
    "05": "��������",
    "06": "�̳�",
    "09": "�ۺ�ҽԺ",
    "12": "����¥",
    "14": "ѧУ",
}

poi_hash_index = {
    "01": 1,
    "05": 2,
    "06": 3,
    "09": 4,
    "12": 5,
    "14": 6,
}

pathCount = 100
pathList = []
csvHeader = ["����", "�������", "�յ�����", "����km", "ͨ��ʱ��minutes",
             "�źŵ�����", "POI_����վ����", "POI_������������",
             "POI_�̳�����", "POI_�ۺ�ҽԺ����", "POI_����¥����", "POI_ѧУ����"]

csvOutputData = []
pois = []
poi_type_list = ["010100|010200|0103000", "050000", "060100|060400|061000", "090100", "120201|120203", "141200"]
path = '..\\data_' + time.strftime('%Y%m%d_%H%M%S') + '.csv'


def generate_path():
    print("1.generate_path")
    counter = pathCount
    while counter > 0:
        counter -= 1

        signalContainer = [[1, 1], [-1, 1], [-1, -1], [1, -1]]
        signal = choice(signalContainer)
        offsetX = round(random.uniform(0.03, 0.07), 6)
        offsetY = round((offsetX - 0.1) / 0.1 * 0.06, 6)
        offsetX *= signal[0]
        offsetY *= signal[1]

        # ���ȣ����������ƶ�
        start_lon = round(random.uniform(lonRange[0], lonRange[1]), 6)
        end_lon = round(random.uniform(lonRange[0], lonRange[1]), 6)
        # end_lon = start_lon + offsetX
        # γ�ȣ��ϱ������ƶ�
        start_lat = round(random.uniform(latRange[0], latRange[1]), 6)
        end_lat = round(random.uniform(latRange[0], latRange[1]), 6)
        # end_lat = start_lat + offsetY

        path = [start_lon, start_lat, end_lon, end_lat]
        print(path)
        pathList.append(path)


def webGetPathPlanningData():
    progress_full = len(pathList)
    for index in range(len(pathList)):
        origin = str(pathList[index][0]) + "," + str(pathList[index][1])
        dest = str(pathList[index][2]) + "," + str(pathList[index][3])
        planning_path_Url = "https://restapi.amap.com/v3/direction/driving?origin=%s&destination=%s&extensions=all&output=json&strategy=16&key=%s" % \
                            (origin, dest, Key)
        # planning_path_Url = "https://restapi.amap.com/v4/direction/bicycling?origin=%s&destination=%s&output=json&key=%s" % \
        print("·����ȡ����:" + str(index + 1) + "/" + str(progress_full) + "[URL]planning_path:" + planning_path_Url)

        res = urlopen(planning_path_Url)
        json_str = res.read().decode('utf-8')
        json_obj = json.loads(json_str)

        print(
            "·����ȡ����:" + str(index + 1) + "/" + str(progress_full) + "[JSON-Response]planning_path:\n" + json_str + "\n")
        planData = []
        planData.append(index + 1)
        planData.append(json_obj['route']['origin'])
        planData.append(json_obj['route']['destination'])
        planData.append(float(json_obj['route']['paths'][0]['distance']) * 0.001)
        planData.append(float(json_obj['route']['paths'][0]['duration']) / 60)
        planData.append(json_obj['route']['paths'][0]['traffic_lights'])
        steps = json_obj['route']['paths'][0]['steps']
        path_poi_dictdata = {}
        for index_step in range(len(steps)):
            pass_point = steps[index_step]['polyline'].split(";")[0]
            poi_data = web_get_passpoi_data(str(index + 1) + "/" + str(progress_full),
                                            str(index_step + 1) + "/" + str(len(steps)), pass_point)
            for index_poi in range(len(poi_data)):
                id = poi_data[index_poi]['id']
                # ��֤ͳ��POIΨһ��
                if id not in path_poi_dictdata:
                    path_poi_dictdata[id] = poi_data[index_poi]
            # break # ���ε���ʹ��
        inncent_poi = {}
        # POI����
        for v in path_poi_dictdata.values():
            typecode = v['typecode'][:2]
            if typecode not in inncent_poi:
                inncent_poi[typecode] = 1
            else:
                inncent_poi[typecode] += 1

        inncent_poi = util.sort_dict_bykey(inncent_poi)
        for k in poi_hash_index.keys():
            if k in inncent_poi:
                planData.append(inncent_poi[k])
            else:
                planData.append(0)

        write_csv_row(planData)
        # csvOutputData.append(planData)


def web_get_passpoi_data(progress, index_step, pass_point):
    type_str = ""
    for i in range(len(poi_type_list)):
        type_str += poi_type_list[i]
        if i < (len(poi_type_list) - 1):
            type_str += "|"
    # pass_point = "116.446404,39.9654"
    url_get_poi = "https://restapi.amap.com/v3/place/around?location=%s&radius=500&types=%s&key=%s" % \
                  (pass_point, type_str, Key)
    # url_get_poi = urllib.parse.quote(url_get_poi)

    print("·��POI��ȡ����:" + progress + "---" + index_step + "--[URL]GetPOIData:", url_get_poi)
    res = urlopen(url_get_poi)
    json_str = res.read().decode('utf-8')
    json_obj = json.loads(json_str)
    print("·��POI��ȡ����:" + progress + "---" + index_step + "[JSON-Response]:\n", json_str, "\n")
    return json_obj["pois"]


def clear_csv():
    print("2.���CSV")
    if os.path.exists(path):
        with open(path, 'r+', newline='') as f:
            f.truncate()


def create_csv(csvOutputData):
    with open(path, 'w+', newline='') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(csvHeader)
        for index in range(len(csvOutputData)):
            csv_write.writerow(csvOutputData[index])


def write_csv(csvOutputData):
    with open(path, 'w+', newline='') as f:
        csv_write = csv.writer(f)
        oldlines = len(f.readlines())
        if oldlines < 1:
            csv_write.writerow(csvHeader)

        for index in range(len(csvOutputData)):
            csv_write.writerow(csvOutputData[index])


def create_header():
    with open(path, 'w+', newline='') as f:
        csv_write = csv.writer(f)
        oldlines = len(f.readlines())
        if oldlines < 1:
            csv_write.writerow(csvHeader)


def write_csv_row(csvRowData):
    with open(path, 'a', newline='') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(csvRowData)


def outputData2CSV(csvOutputData):
    print("3.���CSV")

    if os.path.exists(path):
        write_csv(csvOutputData)
    else:
        create_csv(csvOutputData)


def main():
    startT = time.time()
    print("0.main")
    generate_path()
    create_header()
    # clear_csv()
    webGetPathPlanningData()
    # outputData2CSV(csvOutputData)
    endT = time.time()
    print("��ȡ�ܺ�ʱ��", int((endT - startT)), "��")


main()
