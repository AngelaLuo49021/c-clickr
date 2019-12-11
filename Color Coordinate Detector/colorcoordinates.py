'''
- dont delete my comments bc its code i def do not know how to rewrite
'''
# importing modules

import cv2
import numpy as np
import math
import imutils
import time

# for linux
import pyscreenshot as imageGrab

# for windows and mac
# from PIL import ImageGrab



# create class to store pattern objects
class pattern:
    def __init__(self, id, magenta, cyan, distance):
        self.id = id
        self.top = magenta
        self.bottom = cyan
        self.distance = distance


class coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def rotatePoint(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


# capturing video through webcam
# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
# cap.set(cv2.CAP_PROP_AUTO_WB, 0)

# list of distances found
patternList = []

# can give each distance a unique id???
idCount = 0

while (1):

    image = imageGrab.grab()

    # cv2.imshow("raw", image)

    img = np.array(image)
    orig = img.copy()
    ratio = img.shape[0] / 500.0
    img = imutils.resize(img, height=1000)

    # numpy be weird where blue and red are swapped
    red = img[:, :, 2].copy()
    blue = img[:, :, 0].copy()
    img[:, :, 0] = red
    img[:, :, 2] = blue

    img = cv2.bilateralFilter(img, 9, 75, 75)

    img = cv2.bilateralFilter(img, 11, 75, 75)

    img = cv2.imread('/home/maxwelllwang/c-clickr/testImage3.png', 1)
    # list is cleared for each run through
    patternList = []

    # converting frame(img i.e BGR) to HSV (hue-saturation-value)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # find center of image
    (h, w) = img.shape[:2]
    centerImage = (w // 2, h // 2)

    # definig the range of magenta color
    red_lower = np.array([147, 115, 150], np.uint8)
    red_upper = np.array([150, 255, 255], np.uint8)

    # defining the Range of cyan color
    blue_lower = np.array([87, 115, 150], np.uint8)
    blue_upper = np.array([93, 255, 255], np.uint8)

    # finding the range of magenta,cyan and other colors in the image
    red = cv2.inRange(hsv, red_lower, red_upper)
    blue = cv2.inRange(hsv, blue_lower, blue_upper)

    # Morphological transformation, Dilation
    kernal = np.ones((5, 5), "uint8")

    red = cv2.dilate(red, kernal)
    res = cv2.bitwise_and(img, img, mask=red)

    blue = cv2.dilate(blue, kernal)
    res1 = cv2.bitwise_and(img, img, mask=blue)

    # variables to store the coordinates
    redX = 0
    redY = 0
    blueX = 0
    blueY = 0

    # Tracking the Red Color
    (contours, hierarchy) = cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        redArea = cv2.contourArea(contour)
        if (redArea > 400):
            x, y, w, h = cv2.boundingRect(contour)

            # draws rectangle and label
            # img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
            # cv2.putText(img,"top color",(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255))

            # finds centroid and draws it
            M = cv2.moments(contour)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # cv2.putText(img,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
            redX = center[0]
            redY = center[1]
            cv2.circle(img, center, 2, (0, 0, 0))

            # for each Red contour, loop through blue and compare distance (tested other methods and this works best)
            (contoursBlue, hierarchyBlue) = cv2.findContours(blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for pic, contour in enumerate(contoursBlue):
                blueArea = cv2.contourArea(contour)
                if (abs(blueArea) > 400):
                    x, y, w, h = cv2.boundingRect(contour)
                    # img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                    # cv2.putText(img,"bottom color",(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0))
                    M = cv2.moments(contour)
                    centerBlue = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    # cv2.putText(img,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255, 0, 0),1)
                    blueX = centerBlue[0]
                    blueY = centerBlue[1]
                    cv2.circle(img, centerBlue, 2, (0, 0, 0))

                    # if either coordinate is (0,0) that means it is not found and should not be appended to the list
                    if not (redX == 0 and redY == 0) and not (blueX == 0 and blueY == 0):
                        distance = math.sqrt(((redX - blueX) ** 2) + ((redY - blueY) ** 2))

                        # create object and append to the list
                        # first create two coordinate objects and then add that to the pattern object
                        magenta = coordinates(redX, redY)
                        cyan = coordinates(blueX, blueY)
                        p1 = pattern(idCount, magenta, cyan, distance)
                        patternList.append(p1)
                        idCount = idCount + 1
    # show each distance calculated
    crop_img = img

    crop_img_list = []
    for thing in patternList:
        print
        thing.distance
        # cv2.line(img, (thing.top.x, thing.top.y), (thing.bottom.x, thing.bottom.y), (0,0,0), 5)
        # print("(" + str(thing.top.x) + "," + str(thing.top.y) + ")\t" + "(" + str(thing.bottom.x) + "," + str(thing.bottom.y) + ")\t" + "Distance:" + str(thing.distance))
        colorAngleRad = math.atan2((thing.bottom.y - thing.top.y), (thing.bottom.x - thing.top.x))
        colorAngle = math.degrees(colorAngleRad)

        # rotate
        rot_img = imutils.rotate(img, int(colorAngle))
        (thing.top.x, thing.top.y) = rotatePoint(centerImage, (thing.top.x, thing.top.y), (2 * math.pi) - colorAngleRad)
        (thing.bottom.x, thing.bottom.y) = rotatePoint(centerImage, (thing.bottom.x, thing.bottom.y),
                                                       (2 * math.pi) - colorAngleRad)

        # draws circles around the centroids for visualization
        cv2.circle(rot_img, (int(thing.top.x), int(thing.top.y)), 7, (0, 255, 0), 4)
        cv2.circle(rot_img, (int(thing.bottom.x), int(thing.bottom.y)), 7, (255, 255, 255), 4)

        #cv2.imshow("rotate", rot_img)
        dist = thing.distance
        lengthAdd = float(25) / 64 * dist
        widthAdd = float(25) / 36 * dist

        # print thing.top.y
        try:
            crop_img = rot_img[int(thing.top.y - (lengthAdd)): int(thing.top.y + (lengthAdd)),
                       int(thing.top.x - (widthAdd / 2)): int(thing.top.x + (2 * widthAdd))]
            #cv2.imshow("cropped", crop_img)
            addThis = crop_img
            crop_img_list.append(addThis)
        except:
            continue
    count = 0

    len(crop_img_list)
    # for image in crop_img_list:
    #     try:
    #         # cv2.imshow("cropped #" + str(count), image)
    #         # cv2.imshow("this should look like this" + str(count), crop_img)
    #
    #     except:
    #         crop_img_list.remove(image)
    #         continue
    #     count += 1

    for img in crop_img_list:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(gray, 75, 200)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

        maxArea = 0
        c = 0
        for i in cnts:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            area = cv2.contourArea(i)
            # if area > 1000 / 2:
            #     cv2.drawContours(img, contours, c, (0, 255, 0), 3)
            squares = 0
            if len(approx) == 4:
                squareContours = approx
                c += 1

                (x, y, w, h) = cv2.boundingRect(approx)
                # cv2.putText(img, "top color", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))
                ar = w / float(h)
                print("found")
                # a square will have an aspect ratio that is approximately
                # equal to one, otherwise, the shape is a rectangle
                if ar >= 0.80 and ar <= 1.20:
                    squares += 1

                if area >= maxArea:
                    maxArea = area

                    biggestContour = squareContours

                    print(biggestContour)
                    cv2.drawContours(img, [biggestContour], -1, (0, 255, 0), 2)

                    #warped = four_point_transform(orig, biggestContour.reshape(4, 2) * ratio)
                    # cv2.imshow("Warped", warped)


            # print(squares)

    #cv2.imshow("cropped", imutils.resize(img, height=650))

    # img = cv2.flip(img,1)
    # cv2.imshow("red",res)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        # cap.release()
        cv2.destroyAllWindows()
        break
    # crop_img_list is the list with all the cropped images, crop_img is the image we want to work with