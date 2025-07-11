import cv2
import numpy as np

orb = cv2.ORB_create(500)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

videos = ['Videos/shakyTrain.mp4', 'Videos/stableTrain.mp4']
arrs = {'Videos/shakyTrain.mp4': [], 'Videos/stableTrain.mp4': []}

for i in range(len(videos)):
    cap = cv2.VideoCapture(videos[i])
    prev_kp, prev_des = None, None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp, des = orb.detectAndCompute(gray, None)

        if prev_des is not None and des is not None:
            matches = bf.match(prev_des, des)

            matches = sorted(matches, key=lambda x: x.distance)[:50]

            points_prev = np.float32([prev_kp[m.queryIdx].pt for m in matches])
            points_curr = np.float32([kp[m.trainIdx].pt for m in matches])

            displacement = points_curr - points_prev
            mean_displacement = np.mean(np.linalg.norm(displacement, axis=1))
            arrs[videos[i]].append(mean_displacement)

        prev_kp, prev_des = kp, des

    cap.release()

    print("Input: ", videos[i])
    print("Average inter-frame displacement: ", np.mean(arrs[videos[i]]))
    print("Standard deviation of displacement: ", np.std(arrs[videos[i]]))
    print(" ")