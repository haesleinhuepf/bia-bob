def suggestions():
    return """
    ### Video processing 
        
    * Open .mp4 file and convert it to numpy array
    import cv2
    import numpy as np

    frames = []

    while (ret := cap.read())[0]:
        frames.append(cv2.cvtColor(ret[1], cv2.COLOR_BGR2RGB))

    cap.release()
    video = np.array(frames)  # (frames, height, width, 3)
    """
