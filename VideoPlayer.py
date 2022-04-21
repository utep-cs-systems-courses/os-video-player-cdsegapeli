#!/usr/bin/env python3
import threading
import cv2
import os
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
maxSize = 10

outputDir = 'frames'

# TODO: from imread() add the frame to the queue directly rather than saving to disk
def extract():
    clipName = 'clip.mp4'
    count = 0

    vidcap = cv2.VideoCapture(clipName)

    # if not os.path.exists(outputDir):
    #     print(f"Output directory {outputDir} didn't exist, creating")
    #     os.makedirs(outputDir)

    success, image = vidcap.read()

    print(f'Reading frame {count} {success}')
    while success and count < 72:
        # frame_name = f'frame_{count:04d}.bmp'
        # acquire empty queue spot
        ec_empty.acquire()
        ec_mutex.acquire()
        # cv2.imwrite(f'{outputDir}/{frame_name}', image)
        queue_extract_convert.append(image)
        ec_mutex.release()
        # release the full to signify that there is a frame available for conversion
        ec_full.release()

        # get the next frame
        success, image = vidcap.read()
        print(f'Reading frame {count}')
        count += 1

        # time.sleep(0.5)
    print('Finished extracting frames.')


def convert():
    time.sleep(0.10)
    count = 0
    # acquire a frame from the full queue
    ec_full.acquire()
    ec_mutex.acquire()
    # inFile = f'{outputDir}/{queue_extract_convert[0]}'
    color_frame = queue_extract_convert.pop(0)
    ec_mutex.release()
    # signify that there is a new empty space in the queue
    ec_empty.release()

    # inputFrame = cv2.imread(inFile, cv2.IMREAD_COLOR)

    while color_frame is not None and count < 72:
        print(f'Converting frame {count}')

        grayscale_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)

        # grayFrameName = f'grayscale_{count:04d}.bmp'
        # outFileName = f'{outputDir}/{grayFrameName}'

        cd_empty.acquire()
        cd_mutex.acquire()
        queue_convert_display.append(grayscale_frame)
        # cv2.imwrite(outFileName, grayscaleFrame)
        cd_mutex.release()
        cd_full.release()

        count += 1
        if count == 72:
            break

        ec_full.acquire()
        ec_mutex.acquire()
        # inFile = f'{outputDir}/{queue_extract_convert[0]}'
        color_frame = queue_extract_convert.pop(0)
        ec_mutex.release()
        ec_empty.release()

        # inputFrame = cv2.imread(inFile, cv2.IMREAD_COLOR)
    print("Finished converting frames to grayscale")


def display():
    time.sleep(0.2)
    frameDelay = 42
    count = 0

    # get the name of the first frame
    cd_full.acquire()
    cd_mutex.acquire()
    frame = queue_convert_display.pop(0)
    # frameName = f'{outputDir}/{queue_convert_display.pop(0)}'
    # print(f'pulling frame {frameName} from queue')
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
        # frameName = f'{outputDir}/{queue_convert_display.pop(0)}'
        frame = queue_convert_display.pop(0)
        cd_mutex.release()
        cd_empty.release()

        # frame = cv2.imread(frameName)

    # print('Finished displaying all frames!')
    cv2.destroyAllWindows()


def main():
    extract_thread = threading.Thread(target=extract)
    convert_thread = threading.Thread(target=convert)
    display_thread = threading.Thread(target=display)

    extract_thread.start()
    convert_thread.start()
    display_thread.start()
    # extract()
    # convert()
    # display()


if __name__ == '__main__':
    main()
