from os import listdir
from os.path import isfile, join
import numpy  as np
import argparse
import logging
import time
from task_helper import TaskHelper
from utils.image_reader import ImageReader
from scipy.spatial import distance
import sys
import os
import pandas as pd
from utils.output import Output

import networkx


def Compute_Personalized_PageRank(Subjects, TransitionMatrix, SeedNodeSet):
    Transportation_Probability = 0.85
    TransitionMatrix = np.array(TransitionMatrix)

    Identity_Matrix = np.identity(len(Subjects), dtype=float)
    Coefficient_of_PI = Identity_Matrix - \
                        ((Transportation_Probability) * TransitionMatrix)
    ReSeeding_Vector = np.zeros(len(Subjects))

    P1_Teleportation_Discounting = np.zeros(len(Subjects))
    ReSeeding_Value = 1.0 / len(SeedNodeSet)
    for x in SeedNodeSet:
        ReSeeding_Vector[x - 1] = ReSeeding_Value
    PI_Value = np.dot(np.linalg.inv(Coefficient_of_PI),
                      (1 - Transportation_Probability) * ReSeeding_Vector)
    PI_Value = (PI_Value - min(PI_Value)) / (max(PI_Value) - min(PI_Value))

    P1_ReSeeding_Value = (1 - Transportation_Probability) / len(SeedNodeSet)
    for x in Subjects:
        if x not in SeedNodeSet:
            P1_Teleportation_Discounting[x - 1] = PI_Value[x -
                                                           1] / (Transportation_Probability)
        else:
            P1_Teleportation_Discounting[x - 1] = (
                                                      PI_Value[x - 1] - P1_ReSeeding_Value) / (
                                                  Transportation_Probability)

    P2_Value = P1_Teleportation_Discounting / \
               sum(P1_Teleportation_Discounting)
    Seed_Set_Significance = 0
    for x in SeedNodeSet:
        Seed_Set_Significance += P2_Value[x - 1]
    P3_Value = P2_Value
    for x in SeedNodeSet:
        P3_Value[x - 1] = P1_Teleportation_Discounting[x - 1]
    print("P3 val ", P3_Value)

    return P3_Value
    # x = {}
    # for i, d in enumerate(P3_Value):
    #     x[i + 1] = d
    # x = {k: v for k, v in sorted(
    #     x.items(), key=lambda item: item[1], reverse=True)}
    # return list(x.keys())



def Compute_Personalized_PageRank2(Subjects, TransitionMatrix, SeedNodeSet):
    Transportation_Probability = 0.15
    TransitionMatrix = np.array(TransitionMatrix)
    Identity_Matrix = np.identity(len(Subjects), dtype=float)
    Coefficient_of_PI = Identity_Matrix - \
                        ((Transportation_Probability) * TransitionMatrix)
    ReSeeding_Vector = np.zeros(len(Subjects))

    P1_Teleportation_Discounting = np.zeros(len(Subjects))
    ReSeeding_Value = 1.0 / len(SeedNodeSet)
    for x in range(len(SeedNodeSet)):
        ReSeeding_Vector[x] = ReSeeding_Value
    PI_Value = np.dot(np.linalg.inv(Coefficient_of_PI),
                      (1 - Transportation_Probability) * ReSeeding_Vector)
    PI_Value = (PI_Value - min(PI_Value)) / (max(PI_Value) - min(PI_Value))

    P1_ReSeeding_Value = (1 - Transportation_Probability) / len(SeedNodeSet)
    for x in Subjects:
        if x not in SeedNodeSet:
            P1_Teleportation_Discounting[x - 1] = PI_Value[x -
                                                           1] / (Transportation_Probability)
        else:
            P1_Teleportation_Discounting[x - 1] = (PI_Value[x - 1] - P1_ReSeeding_Value) / (
                                                  Transportation_Probability)

    P2_Value = P1_Teleportation_Discounting / sum(P1_Teleportation_Discounting)
    Seed_Set_Significance = 0
    # for x in SeedNodeSet:
    #     Seed_Set_Significance += P2_Value[x - 1]
    # P3_Value = [[[0]* len(P2_Value)] for i in range(len(P2_Value))]
    P3_Value=P2_Value
    for x in range(len(SeedNodeSet)):
        P3_Value[x] = P1_Teleportation_Discounting[x]
    print("P3 value ",P3_Value)
    x = {}
    for i, d in enumerate(P3_Value):
        x[i + 1] = d
    x = {k: v for k, v in sorted(
        x.items(), key=lambda item: item[1], reverse=True)}
    return P3_Value
    # return list(x.keys())


def calculate_efficiency(image_label_dict, test_all_labels):

    # cf_matrix=confusion_matrix()
    count=0
    for i,j in zip(image_label_dict.values(),test_all_labels):
        if ".png" in i:
            i=i[:-4]
        if ".png" in j:
            j = j[:-4]

        print(j,"-", i)
        if i==j:
            print("===========victory==============")
            count+=1
    print("correct ",count)
    rate = count/len(test_all_labels)
    print("eff. ",rate)

def ppr(teleportation_matrix, random_walk, len_seed, alpha):
    identity_matrix = np.identity(len(random_walk),dtype=float)
    inv = np.linalg.inv(identity_matrix - random_walk)
    pi = np.dot(inv,teleportation_matrix)

    pi = (pi - min(pi)) / (max(pi) - min(pi))

    print("pi",pi)

    # P1_Teleportation_Discounting = np.zeros(len(teleportation_matrix))
    #
    # P1_ReSeeding_Value = (1 - alpha) / len_seed
    # for x in range(len(teleportation_matrix)):
    #     if teleportation_matrix[x][0]==0:
    #         P1_Teleportation_Discounting[x] = pi[x] / (alpha)
    #     else:
    #         P1_Teleportation_Discounting[x] = (pi[x] - P1_ReSeeding_Value) / (
    #                                               alpha)
    # print("p1 teleport discount ", P1_Teleportation_Discounting)
    #
    # P2_Value = P1_Teleportation_Discounting / sum(P1_Teleportation_Discounting)
    #
    # print("p2 val ", P2_Value)
    #
    # Seed_Set_Significance = 0
    # for x in range(len(teleportation_matrix)):
    #     Seed_Set_Significance += P2_Value[x]
    # P3_Value = P2_Value
    #
    #
    # for x in range(len(teleportation_matrix)):
    #     P3_Value[x] = P1_Teleportation_Discounting[x]
    #
    # print("p3 ", P3_Value)
    # return P3_Value
    return pi

def compute_image_feature_map(image_list,feature):
    img_feature_map=dict()
    for i,j in zip(image_list,feature):
        img_feature_map[i]=j.real.tolist()
    return img_feature_map

def calculate_label_images_map(train_images_names, train_all_labels):

    label_images_map = dict()
    for i in range(len(train_all_labels)):
        if train_all_labels[i] in label_images_map:
            label_images_map[train_all_labels[i]].append(train_images_names[i])
        else:
            label_images_map[train_all_labels[i]] = [train_images_names[i]]
    return label_images_map


def compute_seed_matrix(label_images_list,n,image_index_map, alpha=0.85):

    teleportation_matrix = [[0.0 for j in range(1)] for i in range(n)]

    # for i in range(len(label_images_list)):
    #     teleportation_matrix[i][0]=(1-alpha)/len(label_images_list)

    for i in label_images_list:
        teleportation_matrix[image_index_map[i]][0]=(1-alpha)/len(label_images_list)

    teleportation_matrix_np = np.array(teleportation_matrix)
    return teleportation_matrix,teleportation_matrix_np

# def compute_random_walk(image_feature_map,alpha=0.85,kk=10):
#     similarity_matrix=dict()
#
#     # random_walk = [[0.0 for i in range(len(image_feature_map.keys()))] for j in range(len(image_feature_map.keys()))]
#     random_walk=[]
#
#     for image1, feature1 in image_feature_map.items():
#         similar_list=[]
#         for image2, feature2 in image_feature_map.items():
#             if image1!=image2:
#                 # dist = distance.cityblock(feature1,feature2)
#                 similar_list.append(distance.cityblock(feature1,feature2))
#             else:
#                 # dist=0
#                 similar_list.append(0)
#         similar_list_truncated = sorted(similar_list, reverse=True)[:kk]
#         for i in range(len(similar_list)):
#             if similar_list[i] in similar_list_truncated:
#                 similar_list_truncated.remove(similar_list[i])
#             else:
#                 similar_list[i]=0
#
#         similar_list = [(alpha*i)/sum(similar_list) for i in similar_list]
#         random_walk.append(similar_list)
#     random_walk = np.array(list(map(list,zip(*random_walk))))
#
#
#
#
#
#
#
#
#
#     # for image1, feature1 in image_feature_map.items():
#     #     for image2, feature2 in image_feature_map.items():
#     #         if image2 != image1:
#     #             # print('Image1', image1, 'feature1', feature1)
#     #             # print('Image2', image2, 'feature2', feature2)
#     #             dist = distance.cityblock(feature1, feature2)
#     #             # print(image1,image2,dist)
#     #             if image1 in similarity_matrix:
#     #                 similarity_matrix[image1].append(tuple((image2, dist)))
#     #             else:
#     #                 similarity_matrix[image1] = [tuple((image2, dist))]
#     # for image, similarity_list in similarity_matrix.items():
#     #     similarity_matrix[image] = sorted(similarity_matrix[image],
#     #                                                     key=lambda x: x[1])[: kk]
#     #
#     # similarity_matrix = list(map(list, zip(*similarity_matrix)))
#     # similarity_matrix = np.array(similarity_matrix)
#     return random_walk

def similarity_of_a_image(image1,feature1):
    similar_list=[]
    for image2, feature2 in image_feature_map.items():
        if image1 != image2:
            # dist = distance.cityblock(feature1,feature2)
            similar_list.append(distance.cityblock(feature1, feature2))
        else:
            # dist=0
            similar_list.append(0)
    return similar_list


def compute_random_walk(image_feature_map,alpha=0.85,kk=20):
    # random_walk = [[0.0 for i in range(len(image_feature_map))] for j in range(len(image_feature_map))]
    # random_walk = random_walk.to(device)
    random_walk=list()
    for image1, feature1 in image_feature_map.items():
        # print("img : ",image1)
        similar_list=[]
        # ========================================================

        for image2, feature2 in image_feature_map.items():
            if image1!=image2:
                # dist = distance.cityblock(feature1,feature2)
                similar_list.append(distance.cityblock(feature1,feature2))
            else:
                # dist=0
                similar_list.append(0)
            # ----------------------------------------------------------
            # ==========================================================

        similar_list_truncated = sorted(similar_list, reverse=True)[:kk]
        for i in range(len(similar_list)):
            if similar_list[i] in similar_list_truncated:
                similar_list_truncated.remove(similar_list[i])
            else:
                similar_list[i]=0

            # similar_list = [(alpha*i)/sum(similar_list) for i in similar_list]
        summ=sum(similar_list)
        similar_list = [(alpha*i)/summ for i in similar_list]
        random_walk.append(similar_list)

    print("---- %s seconds " % (time.time() - start_time))

    # random_walk = np.array(list(map(list,zip(*random_walk))))
    return random_walk

def associate_labels_to_test_images(test_images_names,labelled_ppr,label_list):

    print("-=========================================")
    for ll in labelled_ppr.keys():
        print("label ",ll)
        print(labelled_ppr[ll])
        print("---------------------------------")

    print("==========================================")
    # label_count=dict()
    query_index_in_label=dict()
    image_label_dict=dict()
    print("label list ",len(label_list))
    for name in test_images_names:
        print("associating for test image ",name)
        for l in label_list:
            # print("label ",l)
            query_index_in_label[l]=-1
            for k in range(len(labelled_ppr[l])):
                # print("+++++++++++++++++++labelled ppr",labelled_ppr[l][k][0])
                if labelled_ppr[l][k][0] == name:
                    query_index_in_label[l] = k
                    break
            print("index in label ppr of ",l," for image ",name," is ",query_index_in_label[l])
        mini = sys.maxsize
        labell = ""
        for lbl, indx in query_index_in_label.items():
            if mini > indx:
                mini = indx
                labell = lbl

        image_label_dict[name] = labell

    return image_label_dict

    # for l in label_list:
    #     label_count[l]=-1
    #     for i in range(len(test_images_names)):
    #         for j in labelled_ppr.keys():
    #             for k in range(len(labelled_ppr[j])):
    #                 if labelled_ppr[j][0] == l:
    #                     label_count[l]=k
    #                     break
    #     mini = 10000
    #     labell=""
    #     for lbl,indx in label_count.items():
    #         if mini>indx:
    #             mini=indx
    #             labell = lbl
    #
    #     image_label_dict[l]=labell
    #
    # return image_label_dict

# def compute_similarity_matrix():

class Task1:
    def __init__(self):
        parser = self.setup_args_parser()
        # input_images_folder_path, feature_model, dimensionality_reduction_technique, reduced_dimensions_count, classification_images_folder_path, classifier
        self.args = parser.parse_args()


    def setup_args_parser(self):
        parser = argparse.ArgumentParser()

        # parser.add_argument('--input_images_folder_path', type=str, required=True)
        # parser.add_argument('--feature_model', type=str, required=True)
        # parser.add_argument('--dimensionality_reduction_technique', type=str, required=True)
        # parser.add_argument('--reduced_dimensions_count', type=int, required=True)
        # parser.add_argument('--classification_images_folder_path', type=str, required=True)
        # parser.add_argument('--classifier', type=str, required=True)

        return parser
logger = logging.getLogger(Task1.__name__)
logging.basicConfig(filename="logs/logs.log", filemode="w", level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

# if __name__=="main":
mypath="all/"

# Read all images

start_time = time.time()
image_reader = ImageReader()

train_path="E:\\projects\\workspace\\1000\\1000"
# train_path="all/"
# test_path="100/100/"

test_path="E:\\projects\\workspace\\100\\100"

train_images = image_reader.get_all_images_in_folder(train_path)
train_images_names = image_reader.get_all_images_filenames_in_folder(train_path)


print("train images name ............. ",len(train_images_names))

train_all_labels = [label.split("-")[1] for label in train_images_names]


print("train label list............. ",len(train_all_labels))
label_list = set()
label_list.update(train_all_labels)
print("label list............. ",len(label_list))


test_files = os.listdir(test_path)

for file in test_files:
    if "test" not in file and "image-" in file:
        splts = file.split(".")
        os.rename(os.path.join(test_path,file),os.path.join(test_path,splts[0]+"-test"+"."+splts[1]))


test_images = image_reader.get_all_query_images_in_folder(test_path)
test_images_names = image_reader.get_all_images_filenames_in_query_folder(test_path)

test_all_labels = [label.split("-")[1] for label in test_images_names]


print(len(test_images))

print(len(test_images[2].matrix))
# combined_images=[]
# combined_image_names=[]

test_labels_for_train = ["test"]*len(test_all_labels)

combined_images = [*train_images,*test_images]

combined_image_names = [*train_images_names,*test_images_names]

# combined_image_names2 = [*train_images_names,*test_labels_for_train]
combined_labels=[*train_all_labels,*test_all_labels]

print(len(combined_images))
print(combined_images[2].matrix)

feature_model="HOG"
dimensionality_reduction_technique="PCA"
k=20

task_helper = TaskHelper()
combined_images = task_helper.compute_feature_vectors(
    feature_model,
    combined_images)

print("Features calculated")
combined_images, drt_attributes = task_helper.reduce_dimensions(
    dimensionality_reduction_technique,
    combined_images,
    k)

print("Dimensions reduced")

rdfv = drt_attributes['reduced_dataset_feature_vector']

print("hi")
print(type(rdfv))
print(len(rdfv))
image_feature_map = compute_image_feature_map(combined_image_names,rdfv)

print("calculated image feature map of length ",len(image_feature_map))

print("combined length ",len(combined_image_names))

label_images_map = calculate_label_images_map(train_images_names,train_all_labels)

# label_images_map = calculate_label_images_map(combined_image_names,combined_labels)
print("mapped label to images")

# time.time()
print("---- %s seconds " % (time.time() - start_time))

print("calculating random walk")
random_walk = compute_random_walk(image_feature_map,0.85)
print("random walk calculated.. for length ",len(random_walk))

labelled_ppr=dict()

image_index_map=dict()
for i,img in enumerate(combined_image_names):
    image_index_map[img]=i

random_walk2 = np.array(random_walk)
G = networkx.from_numpy_array(random_walk2)


print("calculating seed and ppr for each label")
for lbl in label_list:
    if lbl!="test":
        seeds=[]
        for immg in label_images_map[lbl]:
            seeds.append(image_index_map[immg])

        teleportation_matrix,tele_np = compute_seed_matrix(label_images_list=label_images_map[lbl],n=len(random_walk),image_index_map=image_index_map,alpha=0.85)
        # df = pd.DataFrame(ppr(teleportation_matrix,random_walk,len(label_images_map[lbl]),0.15))
        df = pd.DataFrame(ppr(tele_np, random_walk, len(label_images_map[lbl]), 0.85))
        df.insert(0, "Images", combined_image_names)

        # subjects=[i+1 for i in range(len(teleportation_matrix))]
        #    #   ----xxxxx---- df3 = pd.DataFrame(Compute_Personalized_PageRank(subjects,random_walk, label_images_map[lbl]))
        # df3 = pd.DataFrame(Compute_Personalized_PageRank(subjects, random_walk, seeds))
        # df3.insert(0,"Images",combined_image_names)

        # personalization={}
        # for i,t in enumerate(teleportation_matrix):
        #     if t[0]!=0:
        #         personalization[i]=1
        #     else:
        #         personalization[i]=0
        #
        # pagerank_dict = networkx.pagerank(G,0.85,personalization=personalization)
        # pagerank_dict = dict(sorted(pagerank_dict.items()))
        #
        # df2 = pd.DataFrame(np.array(list(pagerank_dict.values())))
        # df2.insert(0,"Images",combined_image_names)

        # print("hi")
        labelled_ppr[lbl] = list(sorted(df.values,key=lambda x:x[1],reverse=True))

image_label_dict = associate_labels_to_test_images(test_images_names,labelled_ppr,label_list)
print("associated labels to test")

print("calculating efficiency")
calculate_efficiency(image_label_dict,test_all_labels)





print("Total run time ....",time.time()-start_time," seconds")

# print(image_feature_map.keys())
# images_label_map = dict()

# Output().save_dict_as_json_file(image_feature_map, "test_tmp/combined_image_feature_map.json")

# transition_matrix = compute_similarity_matrix(image_feature_map)
# print(len(teleportation_matrix))
# print(teleportation_matrix)

# 4000x4000  4000x1             4000x1
#   T         P            S
# image_label_map = dict()