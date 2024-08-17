import cv2 as cv
from ultralytics import YOLO
import numpy as np
import time
from multiprocessing import Process, Queue
from pathlib import Path
import subprocess

from skeleton_generation.utils.skeleton.extractKimiaEDF import generate_skeleton
from skeleton_generation.utils.processing_utils.create_overlay import overlay_images
from skeleton_generation.utils.processing_utils.process_images import process_image

def frame_reader(input_path, frame_queue, num_workers):

    video = cv.VideoCapture(input_path)
    assert video.isOpened(), "Error: Cannot Open Video!"

    frame_index = 0
    while True:
        ret, frame = video.read()
        if not ret:
            # Send sentinel value to signal the end of video frames
            for _ in range(num_workers):
                frame_queue.put(None)
            break
        frame_queue.put((frame_index, frame))
        frame_index += 1
    
    video.release()

    

def process_frame(frame_index, frame, model):
    
    results = model.predict(frame, conf=0.45, save=False, show=False, verbose=False)

    background = frame
    frame_results = []

    for result in results:
        if result is not None:
            img = np.copy(result.orig_img)

            for ci, c in enumerate(result):
                b_mask = np.zeros(img.shape[:2], np.uint8)
                contour = c.masks.xy.pop()
                contour = contour.astype(np.int32)
                contour = contour.reshape(-1, 1, 2)
                _ = cv.drawContours(b_mask, [contour], -1, (255, 255, 255), cv.FILLED)
                mask3ch = cv.cvtColor(b_mask, cv.COLOR_GRAY2BGR)
                isolated = cv.bitwise_and(mask3ch, img)
                processed_img = process_image(isolated)
                skel = generate_skeleton(processed_img["contour_strings"], frame.shape[1], frame.shape[0])
                overlayed = overlay_images(background, skel)

                if overlayed.shape[2] == 4:
                    overlayed = cv.cvtColor(overlayed, cv.COLOR_BGRA2BGR)

                if ci != (len(results[0].boxes) - 1):
                    background = overlayed
                else:
                    frame_results.append(overlayed)
        else:
            frame_results.append(frame)

    return (frame_index, frame_results)

def worker(frame_queue, result_queue, model_path):
    model = YOLO(model_path)  # Load the model within each worker
    while True:
        frame_data = frame_queue.get()
        if frame_data is None:
            result_queue.put(None)
            break
        frame_index, frame = frame_data
        results = process_frame(frame_index, frame, model)
        result_queue.put(results)

def video_writer(output_path, result_queue, frame_count, width, height, fps):
    video_writer = cv.VideoWriter(output_path, cv.VideoWriter_fourcc(*"avc1"), fps, (width, height))

    frames = [None] * frame_count
    finished_frames = 0

    while finished_frames < frame_count:
        frame_data = result_queue.get()
        if frame_data is None:
            # Process remaining frames if any
            continue
        frame_index, frame_results = frame_data
        if frames[frame_index] is None:
            frames[frame_index] = frame_results[0] if frame_results else np.zeros((height, width, 3), dtype=np.uint8)
            finished_frames += 1

    for frame in frames:
        if frame is not None:
            video_writer.write(frame)

    video_writer.release()

def skeletonize(input_path, output_path, file_name):

    model_path = r"backend\skeleton_generation\utils\models\yolov8n-seg.onnx"

    video = cv.VideoCapture(input_path)
    assert video.isOpened(), "Error: Cannot Open Video!"

    frame_count = int(video.get(cv.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv.CAP_PROP_FPS)
    width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))
    video.release()

    frame_queue = Queue()
    result_queue = Queue()

    start_time = time.monotonic()

    num_workers = 9
    reader_process = Process(target=frame_reader, args=(input_path, frame_queue, num_workers))
    reader_process.start()

    workers = []
    for _ in range(num_workers):
        worker_process = Process(target=worker, args=(frame_queue, result_queue, model_path))
        workers.append(worker_process)
        worker_process.start()

    writer_process = Process(target=video_writer, args=(f"{output_path}\\{file_name}", result_queue, frame_count, width, height, fps))
    writer_process.start()

    # Wait for all processes to finish
    reader_process.join()
    for w in workers:
        w.join()
    result_queue.put(None)  # Send sentinel value to video_writer
    writer_process.join()


    print(f"Finished in {time.monotonic() - start_time} seconds")
    cv.destroyAllWindows()
