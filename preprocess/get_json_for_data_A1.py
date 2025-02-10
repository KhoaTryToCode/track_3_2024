#coding:utf-8
import csv
import os
import cv2
import json
import argparse
import glob


shell = {
	"version":"AI CITY 2024 track-3",
	"database":{}
}


_MINUTES_TO_SECONDS=60
_HOURS_TO_SECONDS=3600
def timestamp_to_seconds(timestamp):
    hours, minutes, seconds = map(float, timestamp.split(":"))
    total_seconds = hours * _HOURS_TO_SECONDS + minutes * _MINUTES_TO_SECONDS + seconds
    return total_seconds

local_dict = {
    'Dashboard': 'Dashboard',
    'Rear': 'Rearview',
    'Rearview': 'Rearview',
    'Right': 'RightsideWindow'
}

validata_ids = ['user_id_93491', 'user_id_93542', 'user_id_96269', 'user_id_96371', 'user_id_98067',
                'user_id_98389', 'user_id_99635', 'user_id_99660', 'user_id_99882']

classes = ['Normal Forward Driving',
           'Drinking', 
           'Phone Call(right)', 
           'Phone Call(left)', 
           'Eating',
           'Text (Right)', 
           'Text (Left)', 
           'Reaching behind', 
           'Adjust control panel', 
           'Pick up from floor (Driver)', 
           'Pick up from floor (Passenger)', 
           'Talk to passenger at the right', 
           'Talk to passenger at backseat', 
           'yawning', 
           'Hand on head', 
           'Singing or dancing with music']
# '/path/to/annotations/user_id_93491.csv' obj_path
# {
# 'user_id_93491': {
#     'Dashboard': {
#         'NoAudio_1': '/path/to/dataset/user_id_93491/Dashboard_NoAudio_1.mp4'
#     },
#     'Rearview': {
#         'NoAudio_1': '/path/to/dataset/user_id_93491/Rearview_NoAudio_1.mp4'
#     }
# },
# 'user_id_93542': {
#     'RightsideWindow': {
#         'NoAudio_1': '/path/to/dataset/user_id_93542/RightsideWindow_NoAudio_1.mp4'
#     },
#     'Dashboard': {
#         'NoAudio_2': '/path/to/dataset/user_id_93542/Dashboard_NoAudio_2.mp4'
#     }
# }
# } video_dict

def load_anno_csv(obj_path, video_dict):
    video_list = {}
    with open(obj_path, 'r', encoding='utf-8') as csvfile:
        # Filename,Camera View,Start Time,End Time,Label (Primary)
        # Dashboard_NoAudio_1.mp4,Dashboard,00:00:10,00:00:15,Label_01
        # Rearview_NoAudio_1.mp4,Rearview,00:00:20,00:00:25,Label_02
        # RightsideWindow_NoAudio_1.mp4,Right,00:00:30,00:00:35,Label_03 
        # this is the csv file
        reader = csv.DictReader(csvfile)
        for row in reader:
            video_name = row['Filename'] if ' ' not in row['Filename'] else video_name # Dashboard_NoAudio_1.mp4
            user_id = os.path.basename(obj_path).split('.')[0] # user_id_93491 Again the csv path might just be user_id_93491.csv 
            location = row['Camera View'].replace(' ', '') # Dashboard
            appearance = video_name.split('.')[0].split('_')[-1] # 1
            video_name = video_dict[user_id][location][appearance] # /path/to/dataset/user_id_93491/Dashboard_NoAudio_1.mp4
            video_list.setdefault(video_name, {'annotations': []}) # /path/to/dataset/user_id_93491/Dashboard_NoAudio_1.mp4 and a dictionary with annotations key
            label_id = int(row['Label (Primary)'][6:]) # 1
            label = classes[label_id] # Normal Forward Driving, Classes is on line 33
            segment = [timestamp_to_seconds(row['Start Time']), timestamp_to_seconds(row['End Time'])]
            if segment[0] == segment[1]: # If the start time and end time are the same
                segment[1] += 1 # Add 1 to the end time
            
            if (os.path.basename(video_name).split('.')[0] == 'Right_side_window_user_id_16700_NoAudio_7' and segment[1] > 268) or (os.path.basename(video_name).split('.')[0] == 'Dashboard_user_id_59359_NoAudio_5' and segment[1] > 322): # Some videos have a longer duration than the actual video length
                continue

            video_list[video_name]['annotations'].append({
                'label_id': label_id,  # 1
                'label': label, # Normal Forward Driving
                'segment': segment # [10, 15]
            })
    #     {
    #     '/path/to/dataset/user_id_93491/Dashboard_NoAudio_1.mp4': {
    #         'annotations': [
    #             {
    #                 'label_id': 1,
    #                 'label': 'Drinking',
    #                 'segment': [10.0, 15.0]
    #             }
    #         ]
    #     },
    #     '/path/to/dataset/user_id_93491/Rearview_NoAudio_1.mp4': {
    #         'annotations': [
    #             {
    #                 'label_id': 2,
    #                 'label': 'Phone Call(right)',
    #                 'segment': [20.0, 25.0]
    #             }
    #         ]
    #     }
    # } It should return something like this
    return video_list



def collect_videos(video_path):
    videos = glob.glob(os.path.join(video_path, '*/*.mp4')) # Something/Something.mp4 join with the video_path (/path/to/dataset/)
    # videos is a list of all the videos (mp4 files) in the dataset
    video_dict = {}
    for video in videos:
        user_id, video_name = video.split('/')[-2:] # Slide things in to [path, to, dataset, user_id, video_name.mp4] and [-2:] takes the last two elements
        location = local_dict[video_name.split('_')[0]] # Local dict is on line 23, Dashboard_NoAudio_1.mp4 -> Dashboard
        appearance = video_name.split('.')[0].split('_')[-1] # Dashboard_NoAudio_1.mp4 -> 1
        
        video_dict.setdefault(user_id, {}) # user_id is the key and the value is a dictionary
        video_dict[user_id].setdefault(location, {}) # location is the key and the value is a dictionary
        video_dict[user_id][location][appearance] = video # appearance is the key and the value is the video path
    # {
    # 'user_id_93491': {
    #     'Dashboard': {
    #         'NoAudio_1': '/path/to/dataset/user_id_93491/Dashboard_NoAudio_1.mp4'
    #     },
    #     'Rearview': {
    #         'NoAudio_1': '/path/to/dataset/user_id_93491/Rearview_NoAudio_1.mp4'
    #     }
    # },
    # 'user_id_93542': {
    #     'RightsideWindow': {
    #         'NoAudio_1': '/path/to/dataset/user_id_93542/RightsideWindow_NoAudio_1.mp4'
    #     },
    #     'Dashboard': {
    #         'NoAudio_2': '/path/to/dataset/user_id_93542/Dashboard_NoAudio_2.mp4'
    #     }
    # }
    # }
    # It should return something like this
    return video_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='preprocess')
    
    parser.add_argument('--video_path', metavar='path', required=True,
                        help='the path to the A1 dataset ')   
    parser.add_argument('--label_path', metavar='path', required=True,
                        help='the path to the annotation files of A1')
    parser.add_argument('--output_path', metavar='path', required=True,
                        help='the path to the generated json file')

    args = parser.parse_args()

    train_video_dict = collect_videos(args.video_path) # /path/to/dataset/ this is the video_path

    for label_file in glob.glob(os.path.join(args.label_path, f'*.csv')): # iterating through list of csv files
        #     [
        # '/path/to/annotations/user_id_93491.csv',
        # '/path/to/annotations/user_id_93542.csv'
        #     ] like this one
        user_id = os.path.basename(label_file).split('.')[0] # user_id_93491 This is getting the user ID, it shall reflect that the label file is only user_id_93491.csv not '/path/to/annotations/user_id_93491.csv'
        video_list = load_anno_csv(label_file, train_video_dict)

        for video_path in video_list:
            cap = cv2.VideoCapture(video_path)
            frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_length = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            video_time = frame_length / fps
            
            video_name = os.path.basename(video_path).split('.')[0] # Dashboard_NoAudio_1.mp4 -> Dashboard_NoAudio_1
            video_list[video_path]['resolution'] = f'{frame_w}*{frame_h}' #  Add another key in video_path 1920*1080
            video_list[video_path]['duration'] = video_time # Add another key in video_path 15.0
            video_list[video_path]['subset'] = 'training' if user_id not in validata_ids else 'validation' # Add another key in video_path training or validation
        
            shell['database'][video_name] = video_list[video_path] # Add the video_path dictionary to the shell dictionary
#     {
#     "version": "AI CITY 2024 track-3",
#     "database": {
#         "Dashboard_NoAudio_1": {
#             "annotations": [
#                 {
#                     "label_id": 1,
#                     "label": "Drinking",
#                     "segment": [10.0, 15.0]
#                 }
#             ],
#             "resolution": "1920*1080",
#             "duration": 120.0,
#             "subset": "training"
#         }
#     }
# } It should return something like this
    with open(args.output_path, 'w') as fp:
        json.dump(shell, fp, ensure_ascii=False, indent=4)