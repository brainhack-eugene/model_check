import numpy as np
import os
import nibabel as nib
import re
from nilearn import plotting
from nilearn.image import math_img
import pandas as pd


class Subject(object):
    """
    Data for a subject
    """

    def __init__(self, id, path=None):
        if path is None:
            self.basedir = os.getcwd()
        else:
            self.basedir = path

        self.id = id
        self.con_headers = {}
        self.beta_headers = {}
        self.contrasts = {}
        self.con_data = {}
        self.beta_data = {}



        self.path = os.path.join(self.basedir, "sub-{}".format(id))

        self.con_files = sorted([con for con in os.listdir(self.path) if con.startswith('con')])
        self.beta_files = sorted([beta for beta in os.listdir(self.path) if beta.startswith('beta')])

        self.get_headers()
        self.get_contrasts()

    def get_headers(self):
        self.con_headers = {}
        for c_file in self.con_files:
            self.con_headers[c_file] = {}
            fullpath = os.path.join(self.path, c_file)
            img = nib.load(fullpath)
            for key, val in zip(img.header.keys(), img.header.values()):
                self.con_headers[c_file][key] = val

        self.beta_headers = {}
        for b_file in self.beta_files:
            self.beta_headers[b_file] = {}
            fullpath = os.path.join(self.path, b_file)
            img = nib.load(fullpath)
            for key, val in zip(img.header.keys(), img.header.values()):
                self.beta_headers[b_file][key] = val



    def get_contrasts(self):
        if not self.con_headers:
            self.get_headers()

        for file, header in self.con_headers.items():
            self.contrasts[file] = str(header['descrip']).lstrip('b').strip('\'')




    def find_contrasts(self, pattern, return_contrast=False):
        if not self.contrasts:
            self.get_contrasts()

        good_contrasts =  []
        if return_contrast:
            good_contrasts = {}

        for file, contrast in self.contrasts.items():
            compiled_pattern = re.compile(pattern)

            if bool(compiled_pattern.search(contrast)):
                if return_contrast:
                    good_contrasts[file] = contrast
                else:
                    good_contrasts.append(file)

        return good_contrasts

    def load_contrasts(self, pattern, return_data = False):
        load_files = self.find_contrasts(pattern)

        self.con_data = {}
        for file in load_files:
            self.con_data[file] = nib.load(os.path.join(self.path, file))

        if return_data:
            return self.con_data

    def plot_data(self, con_data=None, pattern=None):
        if pattern:
            con_data = self.load_contrasts(pattern, return_data=True)

        if con_data is None:
            Exception("Need either con_data (loaded from load_contrasts) or regex pattern")

        for filename, con in con_data.items():
            plotting.plot_glass_brain(con, display_mode='lyrz',
                                      colorbar=True, plot_abs=False,
                                      cmap=plotting.cm.ocean_hot, title=self.contrasts[filename])

    def apply_to_pattern(self, pattern, *args):
        """
        args should be a list of functions
        """
        data = self.load_contrasts(pattern, return_data=True)

        #calculated_vals = {}
        all_images_values = []
        for filename, img in data.items():
            single_image_values = [self.id]
            single_image_values.append(filename)
            single_image_values.append(self.contrasts[filename])

            img_data = img.get_fdata()
            img_data = img_data[np.logical_not(np.isnan(img_data))]

            single_image_values.extend([fn(img_data) for fn in args])

            all_images_values.append(single_image_values)

        column_names = ['id', 'filename', 'contrast']
        column_names.extend([fn.__name__ for fn in args])



        df = pd.DataFrame.from_records(all_images_values, columns=column_names)
        return df









if __name__ == "__main__":
    subject_folders = [subdir for subdir in os.listdir(os.path.join(os.getcwd(), 'event')) if subdir.startswith("sub")]
    subject1 = Subject(id='FP001', path='/Users/jonny/git/model_check/event')
    subject.find_contrasts('Look')
    data = subject.load_contrasts('Look', return_data=True)

    data = subject.load_contrasts('Look', return_data=True)

    data = subject.apply_to_pattern("Look", np.mean, np.std, np.min, np.max)

    data = list(data.values())
    math_img("np.mean(img)", img=data)


    plotting.plot_glass_brain(data[list(data.keys())[0]], display_mode='lyrz',
                              colorbar=True, plot_abs=False,
                              cmap=plotting.cm.ocean_hot, title="test")

    ids = ["FP001", "FP002"]
    subjects = [Subject(id=id, path='/Users/jonny/git/model_check/event') for id in ids]
    combo_data = pd.concat([s.apply_to_pattern("Look", np.mean, np.std, np.min, np.max) for s in subjects])

    combo_data = []
    for s in subjects:
        combo_data.append(...)
    combo_data = pd.concat(combo_data)


    subject.get_headers()
    subject.get_contrasts()

    subject.contrasts
    subject.con_headers.keys()
    subject.con_headers['con_0001.nii']









