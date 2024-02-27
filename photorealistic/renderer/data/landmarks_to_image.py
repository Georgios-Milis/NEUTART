import numpy as np
from PIL import Image


def setColor(im, yy, xx, color):
    if len(im.shape) == 3:
        im[yy, xx, 0], im[yy, xx, 1], im[yy, xx, 2] = color[0], color[1], color[2]
    else:
        im[yy, xx] = color[0]

def drawCircle(im, x, y, rad, color=(255,0,0)):
    if x is not None and x.size:
        h, w = im.shape[0], im.shape[1]
        # edge
        for i in range(-rad, rad):
            for j in range(-rad, rad):
                yy = np.maximum(0, np.minimum(h-1, y+i))
                xx = np.maximum(0, np.minimum(w-1, x+j))
                if np.linalg.norm(np.array([i, j])) < rad:
                    setColor(im, yy, xx, color)


def create_eyes_image(A_path, size, transform_scale, add_noise, pts=None):
    w, h = size
    eyes_image = np.zeros((h, w, 3), np.int32)

    if pts is None:
        keypoints = np.loadtxt(A_path, delimiter=" ")
        pts = keypoints[0:14,:].astype(np.int32)

    left_eye_pts = np.concatenate([pts[0:6, :], pts[12:13, :]], axis=0)
    right_eye_pts = np.concatenate([pts[6:12, :], pts[13:14, :]], axis=0)

    if add_noise:
        scale_noise = 2 * np.random.randn(1)
        scale = 1 + scale_noise[0] / 100
        left_eye_mean = np.mean(left_eye_pts, axis=0, keepdims=True)
        right_eye_mean = np.mean(right_eye_pts, axis=0, keepdims=True)
        left_eye_pts = (left_eye_pts - left_eye_mean) * scale + left_eye_mean
        right_eye_pts = (right_eye_pts - right_eye_mean) * scale + right_eye_mean
        # add noise to eyes distance (x dimension)
        d_noise = 2 * np.random.randn(2)
        left_eye_pts[:, 0] += d_noise[0]
        right_eye_pts[:, 0] -= d_noise[1]

    pts = np.concatenate([left_eye_pts, right_eye_pts], axis=0).astype(np.int32)

    # Draw
    """
    face_list = [ [[0,1,2,3], [3,4,5,0]], # left eye
                  [[7,8,9,10], [10,11,12,7]], # right eye
                 ]
    for edge_list in face_list:
            for edge in edge_list:
                for i in range(0, max(1, len(edge)-1)):
                    sub_edge = edge[i:i+2]
                    x, y = pts[sub_edge, 0], pts[sub_edge, 1]
                    curve_x, curve_y = interpPoints(x, y)
                    drawEdge(eyes_image, curve_x, curve_y)
    """
    radius_left = (np.linalg.norm(pts[1]-pts[4]) + np.linalg.norm(pts[2]-pts[5])) / 4
    radius_right = (np.linalg.norm(pts[8]-pts[11]) + np.linalg.norm(pts[9]-pts[12])) / 4
    drawCircle(eyes_image, pts[6, 0], pts[6, 1], int(radius_left))
    drawCircle(eyes_image, pts[13, 0], pts[13, 1], int(radius_right))
    eyes_image = transform_scale(Image.fromarray(np.uint8(eyes_image)))
    return eyes_image
