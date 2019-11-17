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



class Multisubject(object):
    """
    Given a list of subjects, this object behaves like an individual Subject, but returns a dictionary of {subject_id: results}

    eg. you can do
    multisubject.load_contrasts(...) just like subject.load_contrasts(...)

    Multisubjects is also subscriptable -- you can index the 0:2th subjects, as well as index by single or lists of subject ids

    eg.
    multisubject[0:2].load_contrasts(...)
    multisubject['sub_id_1'].load_constrasts(..)
    multisubject[['sub_id_1', 'sub_id_2']].load_contrasts(...)

    """
    def __init__(self, subjects):
        self.subjects = subjects
        self.subject_ids = [s.id for s in self.subjects]

    def __getattr__(self, name):
        attrs = [object.__getattribute__(sub, name) for sub in self.subjects]
        if hasattr(attrs[0], '__call__'):
            def newfunc(*args, **kwargs):
                result = {}
                for method, id in zip(attrs, self.subject_ids):
                    result[id] = method(*args, **kwargs)
                return result

            return newfunc
        else:
            return attrs

    def __getitem__(self, item):
        if isinstance(item, str) or isinstance(item, bytes):
            return_val = [s for s in self.subjects if s.id == item]
        if isinstance(item, list):
            return_val = [s for s in self.subjects if s.id in item]
        else:
            return_val = self.subjects[item]
        if isinstance(return_val, list):
            return Multisubject(return_val)
        else:
            return return_val




multisub = Multisubject(subjects=subjects)

multisub[0:2].load_contrasts('Look', return_data=True)


class Foo(object):
    def __getattribute__(self,name):
        attr = object.__getattribute__(self, name)
        if hasattr(attr, '__call__'):
            def newfunc(*args, **kwargs):
                print('before calling %s' %attr.__name__)
                result = attr(*args, **kwargs)
                print('done calling %s' %attr.__name__)
                return result
            return newfunc
        else:
            return attr





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

    ids = ["FP001", "FP002", "FP001"]
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












