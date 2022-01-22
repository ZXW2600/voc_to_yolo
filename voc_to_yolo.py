#! python3
# -*- encoding: utf-8 -*-
'''
@File   		:   read_list.py
@Time    		:   2022/01/22 14:14:29
@Author  		:   ZXW2600
@Version 		:   1.0
@Contact 		:   zhaoxiwnei74@gmail.com
@description	:
'''
import os
import json
from lxml import etree
# from glob import iglob
from pathlib import Path
import argparse
import csv
import yaml

labels = {}
categories = {}


def convert(img_size, coords):
    """Convert from xmin,xmax,ymin,ymax to xywh normalised format
    Args:
        img_size(array): array of (img_width, img_height)
        coords(array): Array of class_id, xmin, xmax, ymin, ymax
    Returns:
        xywh(array): Array of normalised xywh coords
    """
    img_width = img_size[0]
    img_height = img_size[1]
    # Calculate Bounding box dimensions from xml
    class_id = str(coords[0])
    x_centre = str(((coords[1]+coords[2])/2)/img_width)
    y_centre = str(((coords[3]+coords[4])/2)/img_height)
    height = str((coords[4]-coords[3])/img_height)
    width = str((coords[2]-coords[1])/img_width)

    xywh = (class_id, x_centre, y_centre, width, height)
    return xywh


def voc_xml2yolo_txt(xml_path, txt_path):
    with open(txt_path, 'w') as txtfile:
        with open(xml_path) as file:
            print(f'Processing file {Path(xml_path).name}...')
            # create annotations object
            annotations = etree.fromstring(file.read())
            # extract elements that are needed
            image_size = annotations.find('size')
            image_width = float(image_size.find('width').text)
            image_height = float(image_size.find('height').text)
            boxes = annotations.iterfind('object')
            for box in boxes:
                annotation_list = []
                # Extract bounding box pixel data
                bndbox = box.find('bndbox')
                xmin = float(bndbox.find('xmin').text)
                ymin = float(bndbox.find('ymin').text)
                xmax = float(bndbox.find('xmax').text)
                ymax = float(bndbox.find('ymax').text)

                label_name = box.find('name').text
                if label_name not in labels:
                    labels[label_name] = len(labels)
                class_id = labels[label_name]
                categories[class_id] = label_name
                # send off for conversion
                xywh = convert((image_width, image_height),
                               (class_id, xmin, xmax, ymin, ymax))
                annotation_list.extend(xywh)
                line = ' '.join(annotation_list)
                txtfile.write(f'{line}\n')
    txtfile.close()


def cvt_list(voc, yolo, output_folder):
    f_input = open(voc, 'r')
    f_output = open(yolo, 'w')
    with f_input, f_output:
        reader = csv.reader(f_input, delimiter=" ")
        i = 0
        for row in reader:
            # 打印日志
            i = i+1
            print(i, end=": ")
            voc_image_path =  os.path.join(args.input,row[0])
            voc_annotation_path = os.path.join(args.input,row[1])
            print("image:   "+voc_image_path +
                  "      annotation:  "+voc_annotation_path)
            # 写入yolo划分数据
            f_output.write("./images/"+Path(voc_image_path).name+"\n")

            yolo_image_path = os.path.join(
                output_folder, "images/"+Path(voc_image_path).name)
            yolo_annotation_path = os.path.join(
                output_folder, "labels/"+Path(voc_image_path).stem+".txt")
            print("     image:   "+yolo_image_path +
                  "          txt:  "+yolo_annotation_path)
            # 转化VOC数据到yolo
            voc_xml2yolo_txt(voc_annotation_path, yolo_annotation_path)


def write_yolo_yaml(path, dataset_path, train_list_path, val_list_path, test_list_path):
    dataset = {}
    dataset["path"] = dataset_path
    dataset["train"] = train_list_path
    dataset["val"] = val_list_path
    dataset["test"] = test_list_path
    dataset["nc"] = len(labels)
    names=[]
    for key,value in categories.items():
        names.append(value)
    dataset["names"] = names
    with open(path, 'w') as file:
        yaml.dump(dataset, file)


def main():

    train_list_path = os.path.join(args.input, 'train_list.txt')
    val_list_path = os.path.join(args.input, 'val_list.txt')
    test_list_path = os.path.join(args.input, 'test_list.txt')

    if not os.path.exists(os.path.join(args.output, 'labels')):
        os.mkdir(os.path.join(args.output, 'labels'))
    if not os.path.exists(os.path.join(args.output, 'images')):
        os.mkdir(os.path.join(args.output, 'images'))

    train_list_output_path = os.path.join(args.output, 'yolo_train_list.txt')
    val_list_output_path = os.path.join(args.output, 'yolo_val_list.txt')
    test_list_output_path = os.path.join(args.output, 'yolo_test_list.txt')

    yaml_output_path = os.path.join(args.output, 'dataset.yaml')

    cvt_list(train_list_path, train_list_output_path, args.output)
    cvt_list(val_list_path, val_list_output_path, args.output)

    if Path(test_list_path).exists():
        cvt_list(test_list_path, test_list_output_path, args.output)
    else:
        print("didn't find test list! skip it!")
        test_list_output_path=[]

    print(categories)


    write_yolo_yaml(yaml_output_path, args.output, train_list_output_path, val_list_output_path,
                    test_list_output_path)
    print("Data processing finished! Start copy image from " +
          args.input + "/JPEGImage to "+args.output+"/images")
    print("cp -r "+os.path.join(args.input, 'JPEGImages ') +
          os.path.join(args.output, 'images'))
    os.system("cp -r "+os.path.join(args.input, 'JPEGImages/* ') +
              os.path.join(args.output, 'images/'))
    print("all finished!")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str,
                        default='data/input',
                        help='Directory location of your VOC, where JPEGImage and Annotations located, assumed train_list.txt and val_list.txt exist',
                        required=True)
    parser.add_argument('--output', type=str,
                        default='data/output',
                        help='Directory location you want your output yolo dataset',
                        required=True)
    args = parser.parse_args()
    main()
