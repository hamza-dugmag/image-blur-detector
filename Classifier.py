# Hamza Dugmag - 2019
# Classifier.py

# import required libraries
from tkinter import filedialog
from tkinter import *
import cv2
import os


class BlurClassifier(object):

    def __init__(self):
        """Initialize class"""

        # classifier configurations
        self.directory = None
        self.sensitivity = None
        self.log = "/BlurryImagesLog.txt"

        # list of blurry images
        self.defective = []

        # dynamic widgets
        self.entry_sensitivity = None

        # top-level GUI widget; window
        self.root = Tk()
        self.root.resizable(False, False)
        self.root.title("/")

        self.ConstructGUI()

    def ConstructGUI(self):
        """Layout widgets and initialize status bar"""

        # text widgets
        label_select = Label(self.root, text="Select Directory: ")
        label_select.grid(row=1, column=1, sticky=E)

        label_sensitivity = Label(
            self.root,
            text="Sensitivity (1.0 to 5.0): \n(3.0 recommended)"
        )
        label_sensitivity.grid(row=2, column=1, sticky=E)

        # separator widget
        padding = 40

        frame_left = Frame(self.root, width=padding)
        frame_left.grid(row=0, column=0)

        frame_right = Frame(self.root, width=padding)
        frame_right.grid(row=0, column=3)

        frame_top = Frame(self.root, height=padding)
        frame_top.grid(row=0, column=1)

        frame_bottom = Frame(self.root, height=padding)
        frame_bottom.grid(row=5, column=1)

        frame_middle = Frame(self.root, height=padding)
        frame_middle.grid(row=3, column=1)

        # entry widgets
        self.entry_sensitivity = Entry(self.root, width=5)
        self.entry_sensitivity.grid(row=2, column=2, sticky=W)

        # button widgets
        button_browse = Button(
            self.root,
            text="Browse",
            command=self.SelectDirectory
        )
        button_browse.grid(row=1, column=2, sticky=W)

        button_run = Button(
            self.root,
            text="Run Classifier",
            command=self.AnalyzeDirectory
        )
        button_run.grid(row=4, column=1)

        button_log = Button(self.root, text="Open Log", command=self.OpenLog)
        button_log.grid(row=4, column=2)

        # create status bar
        self.SetStatusBar()

        # run widget; open window
        self.root.mainloop()

    def SetStatusBar(self, text="Configure classifier."):
        """Set status bar text"""

        status = Label(
            self.root,
            text=text,
            bd=1,
            relief=SUNKEN,
            anchor=W,
            width=30
        )
        status.grid(row=6, columnspan=4, column=0)

    def SelectDirectory(self):
        """Button widget function to select
        directory for image classification
        """

        # Windows Explorer dialog to select directory for analysis
        path = filedialog.askdirectory()

        # update directory and window title
        if len(path) > 0:
            self.directory = path

            self.root.title(self.directory[self.directory.rfind("/"):])
            self.SetStatusBar()

    def AnalyzeDirectory(self):
        """Classify all images in a specified directory based on blur"""

        # do not analyze if no directory specified
        if self.directory is None or len(self.directory) == 0:
            self.SetStatusBar("Select a directory.")
            return None

        # do not analyze if sensitivity not specified or out of range
        try:
            self.sensitivity = float(self.entry_sensitivity.get())

            if self.sensitivity < 1.0 or self.sensitivity > 5.0:
                raise Exception
        except Exception:
            self.SetStatusBar("Select a sensitivity.")
            return None

        # reset defective image list
        self.defective = []

        # classify all images in directory and produce log file
        for file in self.GetNextImage():
            self.ClassifyImage(file)

        self.SetStatusBar("Done!")
        self.GenerateLog()

    def GetNextImage(self):
        """Retrieve absolute path of the next valid image in a directory"""

        # valid file extentions of images
        filetypes = (".png", ".jpg", ".bmp", ".tiff", ".gif")

        for dirpath, _, filenames in os.walk(self.directory):
            for file in filenames:
                if file.lower().endswith(filetypes):
                    # yeild absolute file path if is an image
                    yield os.path.abspath(os.path.join(dirpath, file))

    def ClassifyImage(self, file):
        """Determine whether image is blurry
        or clear according to sensitivity
        """

        # set blur threshold based on sensitivity and compute focus measure
        threshold = 2**(self.sensitivity + 4.4)
        focusMeasure = self.LaplacianVariance(file)

        # append to list of blurred images if below threshold
        if focusMeasure < threshold:
            self.defective.append(file)

    def LaplacianVariance(self, file):
        """Compute focus measure of image using variance of Laplacian method"""

        # read image
        image = cv2.imread(file)

        # resize image if too big to reduce excess sensitivity
        maxWidth = 500
        width = image.shape[1]
        if width > maxWidth:
            resizeFactor = maxWidth / width
            image = cv2.resize(image, (0, 0), fx=resizeFactor, fy=resizeFactor)

        # convert to grayscale and calculate focus measure
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        focusMeasure = cv2.Laplacian(grayscale, cv2.CV_64F).var()

        print(image.shape[1], file, focusMeasure)  # DEBUG

        return focusMeasure

    def GenerateLog(self):
        """Generate text file of defective image
        addresses in specified directory
        """

        # create log file
        fileHandle = open(self.directory + self.log, "w")

        # list absolute paths of blurry images
        for path in self.defective:
            fileHandle.write(path + "\n")

        fileHandle.close()

    def OpenLog(self):
        """Open generated text file in operating system text editor"""

        try:
            os.startfile(self.directory + self.log)
        except Exception:
            pass  # ignore if no directory specified


# run program on startup
BlurClassifier()
