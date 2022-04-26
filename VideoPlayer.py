#!/usr/bin/env python3

import threading
import cv2
import time


# semaphores for the producers and consumers
ec_empty = threading.Semaphore(10)
ec_full = threading.Semaphore(0)

cd_empty = threading.Semaphore(10)
cd_full = threading.Semaphore(0)

ec_mutex = threading.Lock()
cd_mutex = threading.Lock()

queue_extract_convert = []
queue_convert_display = []


def extract():
    clipName = 'clip.mp4'
    count = 0

    vidcap = cv2.VideoCapture(clipName)

    success, image = vidcap.read()

    print(f'Reading frame {count} {success}')
    while success and count < 72:

        # acquire empty queue spot
        ec_empty.acquire()
        ec_mutex.acquire()
        queue_extract_convert.append(image)
        ec_mutex.release()
        # release the full to signify that there is a frame available for conversion
        ec_full.release()

        # get the next frame
        success, image = vidcap.read()
        print(f'Reading frame {count}')
        count += 1

    print('Finished extracting frames.')


def convert():
    time.sleep(0.10)
    count = 0
    # acquire a frame from the full queue
    ec_full.acquire()
    ec_mutex.acquire()
    color_frame = queue_extract_convert.pop(0)
    ec_mutex.release()
    # signify that there is a new empty space in the queue
    ec_empty.release()

    while color_frame is not None and count < 72:
        print(f'Converting frame {count}')

        grayscale_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)

        cd_empty.acquire()
        cd_mutex.acquire()
        queue_convert_display.append(grayscale_frame)
        cd_mutex.release()
        cd_full.release()

        count += 1
        if count == 72:
            break

        ec_full.acquire()
        ec_mutex.acquire()
        color_frame = queue_extract_convert.pop(0)
        ec_mutex.release()
        ec_empty.release()

    print("Finished converting frames to grayscale")


def display():
    time.sleep(0.2)
    frameDelay = 42
    count = 0

    # get the name of the first frame
    cd_full.acquire()
    cd_mutex.acquire()
    frame = queue_convert_display.pop(0)
    cd_mutex.release()
    cd_empty.release()



    while frame is not None:
        print(f'Displaying frame {count}')

        cv2.imshow('Video', frame)

        if cv2.waitKey(frameDelay) and 0xFF == ord("q"):
            break

        count += 1
        if count == 72:
            print('Finished displaying all frames!')
            break

        cd_full.acquire()
        cd_mutex.acquire()
        frame = queue_convert_display.pop(0)
        cd_mutex.release()
        cd_empty.release()

    cv2.destroyAllWindows()


def main():
    extract_thread = threading.Thread(target=extract)
    convert_thread = threading.Thread(target=convert)
    display_thread = threading.Thread(target=display)

    extract_thread.start()
    convert_thread.start()
    display_thread.start()


if __name__ == '__main__':
    main()
