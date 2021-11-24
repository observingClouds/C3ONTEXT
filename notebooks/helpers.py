"""
Helper functions for Agreement_manual_NN.ipynb
"""
import pandas as pd
import matplotlib.cm as cm
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

def iou_one_class_from_annos(arr1, arr2, return_iou=False):
    """
    Returns the IoU from lists of [x, y, w, h] annotations.
    Image size must be given because arrays are created internally.
    If return_iou is True, the actual IoU score is computed,
    otherwise i, u will be returned.
    
    >>> iou_one_class_from_annos([False,True],[False,False],return_iou=True)
    0.0
    >>> iou_one_class_from_annos([False,True],[True,False],return_iou=True)
    0.0
    >>> iou_one_class_from_annos([False,True],[True,True],return_iou=True)
    0.5
    >>> iou_one_class_from_annos([False,False],[False,False],return_iou=True)
    np.nan
    
    """
    i = intersect_from_arrs(arr1, arr2)
    u = union_from_arrs(arr1, arr2)
    if return_iou:
        if u > 0:
            return i/u
        # only exists in one of the inputs
        elif u == 0 and np.any([arr1, arr2]):
            return 0
        # no identifications in any input
        else:
            return np.nan
    else:
        return i, u


def intersect_from_arrs(arr1, arr2):
    """Applies bitwise_and followed by a sum. Note that the sum operation is expensive."""
    return np.count_nonzero(np.bitwise_and(arr1, arr2))


def union_from_arrs(arr1, arr2):
    """Applies bitwise_or followed by a sum. Note that the sum operation is expensive."""
    return np.count_nonzero(np.bitwise_or(arr1, arr2))


def get_date_from_filename(fn):
    fn_parts = fn.split('/')
    try:
        date = dt.datetime.strptime(fn_parts[-1].split('_')[4], 'Day%Y%m%d')
    except ValueError:
        date = dt.datetime.strptime(fn_parts[-1].split('_')[-3], 'TrueColor%Y%m%d')
    return date


def create_mask(boxes, labels, out, label_map={'Sugar':0, 'Fish': 3, 'Flower': 2, 'Gravel': 1}):
    """
    Create or add mask to array
    """
    xy_boxes = [wh2xy(*b) for b in boxes]
    
    for l, lab in enumerate(labels):
        mask_layer = label_map[lab]
        x1,y1,x2,y2 = np.array(xy_boxes[l]).astype(int)
        out[x1:x2,y1:y2,mask_layer] = True
    
    return out


def interSection(arr1,arr2): # finding common elements
    values = list(filter(lambda x: x in arr1, arr2))
    return values


def merge_mask(mask):
    """Merge mask along time dimension (has to be first dimension)
    """
    return np.any(~np.isnan(mask.astype("float")), axis=0)


def identify_where_class_missing(arr1,arr2):
    """
    Identify which input array does not contain
    any labels.
    >>> identify_where_class_missing([[True, False],[True, False]],[[False, False],[False, False]])
    2
    >>> identify_where_class_missing([False],[True])
    1
    >>> identify_where_class_missing([False],[False])
    3
    >>> identify_where_class_missing([True],[True])
    0
    """
    missing_arr1 = not np.any(arr1)
    missing_arr2 = not np.any(arr2)
    if not missing_arr1 and not missing_arr2:
        return 0
    elif missing_arr1 and not missing_arr2:
        return 1
    elif missing_arr2 and not missing_arr1:
        return 2
    elif missing_arr1 and missing_arr2:
        return 3
    

def plot_clustered_stacked(dfall, labels=None, title="multiple stacked bar plot",  H="/", color_dict={None}, **kwargs):
    """Given a list of dataframes, with identical columns and index, create a clustered stacked bar plot. 
labels is a list of the names of the dataframe, used for the legend
title is a string for the title of the plot
H is the hatch used for identification of the different dataframe"""

    n_df = len(dfall)
    n_col = len(dfall[0].columns) 
    n_ind = len(dfall[0].index)
    axe = plt.subplot(111)

    for df in dfall : # for each data frame
        axe = df.plot(kind="bar",
                      linewidth=0,
                      stacked=True,
                      ax=axe,
                      legend=False,
                      grid=False,
                      color=color_dict,
                      **kwargs)  # make bar plots

    h,l = axe.get_legend_handles_labels() # get the handles we want to modify
    for i in range(0, n_df * n_col, n_col): # len(h) = n_col * n_df
        for j, pa in enumerate(h[i:i+n_col]):
            for rect in pa.patches: # for each index
                rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col))
                if H is not None:
                    rect.set_hatch(H * int(i / n_col)) #edited part
                rect.set_edgecolor('white')
                rect.set_width(1 / float(n_df + 1))

    axe.set_xticks(((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)[::2])
    axe.set_xticks(((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.), minor=True)
    axe.set_xticklabels(df.index.date[::2], rotation = 90)
    axe.set_title(title)

    # Add invisible data to add another legend
    n=[]        
    for i in range(n_df):
        if H is None:
            n.append(axe.bar(0, 0, color="gray", edgecolor='white'))
        else:
            n.append(axe.bar(0, 0, color="gray", hatch=H * int(i), edgecolor='white'))

    l1 = axe.legend(h[:n_col], l[:n_col], loc=[1.01, 0.5])
    if labels is not None:
        l2 = plt.legend(n, labels, loc=[1.01, 0.1]) 
    axe.add_artist(l1)
    return axe