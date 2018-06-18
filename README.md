# DLIB-faceRecognition

![Alt text](demo.gif?raw=true "Title")


This is a face recognition sample using DLIB.

## Compatibility
The code is tested using DLIB 19.10.0 under Ubuntu 16.04 with Python 3.6.5. 

Other needed libraries are below.

| Name | Version |
|----------|--------|
|google-api-python-client |1.7.1 |
|google-auth              |1.5.0  |  
|google-auth-httplib2     |0.0.3   | 
|httplib2                 |0.11.3   |
|mkl-fft                  |1.0.0    |
|mkl-random               |1.0.1    |
|numpy                    |1.14.3   |
|oauth2client             |4.1.2    |
|opencv-contrib-python    |3.4.1.15 |
|Pillow                   |5.1.0    |
|PyAudio                  |0.2.11   |
|PyDrive                  |1.3.1    |
|PyYAML                   |3.12     |
|rsa                      |3.4.2    |
|six                      |1.11.0   |



## News
| Date     | Update |
|----------|--------|
| 2018-06-06 | Released a first version.|

## Inspiration
The code is heavily inspired by the [face_recognition](https://github.com/ageitgey/face_recognition) implementation.


## How to run
Simply run the command `python facerec_dlib.py`.

```bash
$ python facerec_dlib.py
```

Beforehand, you must put face images into 'faces' folder.

```bash
faces
  |
  |--name1
  |   |--face1.jpg
  |   |--face2.jpg
  |--name2
  |   |--face1.jpg
  |   |--face2.jpg
  |   |--face2.jpg
  |   |--black   <- specify that this person is black-listed.
  |--name3
      |--face1.jpg
      |--face2.jpg
      |--vip     <- specify that this person is vip-listed.
```

To quit, press 'q' key, 

