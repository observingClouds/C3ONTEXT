import numpy as np
import pandas as pd
import datetime as dt

def add_subject_set_id_to_clas_df(clas_df, subj_df, subjs_of_interest):
    """
    Basically to get the filename to the clas_df
    """
    s = subj_df.set_index('subject_id')
    # HARDCODED: Only using the actual datasets, not practice, etc.
    s = s[s.subject_set_id.apply(lambda s: s in subjs_of_interest)]
#     import pdb; pdb.set_trace()
    clas_df['subject_set_id'] = clas_df.subject_ids.apply(
        lambda i: s.loc[i].subject_set_id if i in list(s.index) else np.nan)
    clas_df.dropna(subset=['subject_set_id'], inplace=True)
    # Also add filename
    filenames = clas_df.subject_ids.apply(lambda i: s.loc[i].metadata['file'][48:])
    clas_df['fn'] = filenames
    return clas_df


def clean_tool_label(label):
    """
    >>> t="Sugar ![thumb_sugar.jpeg](https://panoptes-upl"
    >>> clean_tool_label(t)
    'Sugar'
    """
    if label is not None:
        return label[:label.find('!')-1]
    else:
        return None


def restrict_to_version(clas_df, version_dict):
    """
    Remove classifications from certain workflow
    that do not have the requested version number.
    """
    mask = clas_df.apply(lambda i: i.workflow_version in version_dict[i.workflow_id], axis=1)
    clas_df = clas_df.drop(clas_df.loc[~mask].index)
    return clas_df


def limit_classifications_to_domain(coords, imag_dim):
    """
    Classifications can be larger than
    the the image itself.
    >>> limit_classifications_to_domain([-10,-10,2300,1600], (2200,1500))
    (0, 0, 2200, 1500)
    >>> limit_classifications_to_domain(coords=[-10,20,20,1600], imag_dim=(2200,1500))
    (0, 20, 10, 1480)
    """
    x = coords[0]
    y = coords[1]
    w = coords[2]
    h = coords[3]
    
    if x < 0:
        w = w-np.abs(x)
        x = 0
    if y < 0:
        h = h-np.abs(y)
        y = 0
    if x+w > imag_dim[0]:
        w = w - ((w+x)-imag_dim[0])
    if y+h > imag_dim[1]:
        h = h - ((h+y)-imag_dim[1])
    return x, y, w, h


def get_user_statistics(df):
    results = {}
    workflows = np.unique(df.workflow_name)
    for user, user_df in df.groupby('user_name'):
        results[user] = len(np.unique(user_df.classification_id))
    return results


def convert_clas_to_annos_df(clas_df):
    """
    Converts a classification pd.DataFrame parsed from the raw Zooniverse file to a pd.DataFrame
    that has one row per bounding box. 
    Additionally, extracts coordinate and metadata information
    """
    # We need to figure out first how many items we have in order to allocate the new DataFrame
    count = 0
    for i, row in clas_df.iterrows():
        if len(row.annotations['value']) == 0: count += 1
        for anno in row.annotations['value']:
            count += 1
    # Allocate new dataframe
    annos_df = pd.DataFrame(
        columns=list(clas_df.columns) + ['x', 'y', 'width', 'height', 'tool_label',
                                         'started_at', 'finished_at', 'already_seen'],
        index=np.arange(count)
    )
    # go through each annotation
    j = 0
    for i, row in clas_df.iterrows():
        coords = row.annotations['value']
        if len(coords) == 0:
            coords = [{'x': None, 'y': None, 'width': None, 'height': None, 'tool_label': None, 'already_seen': None}]
        for anno in coords:
            for c in clas_df.columns:
                annos_df.iloc[j][c] = row[c]
            for coord in ['x', 'y', 'width', 'height', 'tool_label']:
                annos_df.iloc[j][coord] = anno[coord]
            for meta in ['started_at', 'finished_at']:
                annos_df.iloc[j][meta] = row.metadata[meta]
            annos_df.iloc[j]['already_seen'] = row.metadata['subject_selection_state']['already_seen']
            j += 1
    # Convert start and finish times to datetime
    for meta in ['started_at', 'finished_at']:
        annos_df[meta] = pd.to_datetime(annos_df[meta])
    return annos_df


def decode_filename_eurec4a(filename):
    """
    Decode filenames of EUREC4A workflows
    """
    return_dict = {}
    basename = filename.split('/')[-1]
    basename_spl = basename.split('_')
    if 'GOES16' in basename:
        return_dict['platform'] = 'GOES16'
        return_dict['instrument'] = 'ABI'
        return_dict['channel'] = basename_spl[1]
        return_dict['date'] = dt.datetime.strptime(''.join(basename_spl[2:4]), "%Y%m%d%H%M.jpeg")
        return_dict['init_date'] = pd.NaT
    elif 'MODIS' in basename:
        return_dict['platform'] = basename_spl[0]
        return_dict['instrument'] = 'MODIS'
        return_dict['channel'] = 'CorrectedReflectance'
        return_dict['date'] = dt.datetime.strptime(''.join(basename_spl[4:6]), "TrueColor%Y%m%d%H%M%S")
        return_dict['init_date'] = pd.NaT
    elif 'ICON' in basename:
        return_dict['platform'] = 'ICON'
        return_dict['instrument'] = 'n/a'
        return_dict['channel'] = 'n/a'
        return_dict['date'] = dt.datetime.strptime(basename_spl[4], "%Y%m%d%H%M.jpeg")
        return_dict['init_date'] = dt.datetime.strptime(basename_spl[3], "%Y%m%d%H")
        return_dict['variable/channel'] = basename_spl[2]
    elif len(basename) == 0:
        return_dict['init_date'] = pd.NaT
        return_dict['date'] = pd.NaT
        return_dict['instrument'] = None
    else:
        print(basename)
        raise ValueError(basename)
    return return_dict


def rle (binary_mask,return_str=True):
    """
    Fast run length encoding
    
    adapted from https://www.kaggle.com/hackerpoet/even-faster-run-length-encoder
    """
    flat_mask = binary_mask.flatten()

    starts = np.array((flat_mask[:-1] == 0) & (flat_mask[1:] == 1))
    ends = np.array((flat_mask[:-1] == 1) & (flat_mask[1:] == 0))
    starts_ix = np.where(starts)[0] + 2
    ends_ix = np.where(ends)[0] + 2
    lengths = ends_ix - starts_ix
    
    if return_str:
        encoding = ''
        for idx in range(len(starts_ix)):
            encoding += '%d %d ' % (starts_ix[idx], lengths[idx])
        return encoding
    else:
        return starts_ix, lengths


def most_common_boxes(boxes, visualize=False, return_all_pattern=False, imag_dim=(2100,1400)):
    """
    Combine most common boxes of one image
    into one grid
    """
    pattern_dic = {'Sugar': 0, 'Flower': 1, 'Fish': 2, 'Gravel': 3}
    
    grid = np.zeros((imag_dim[0],imag_dim[1],4),dtype="int")
    for b,box in enumerate(boxes):
        # Get coordinates of single label
        if not all(box): continue
        coords = np.round(box[0:4].astype(float),0).astype(int)
        x0 = coords[0]
        y0 = coords[1]
        # restrict x1,y1 to domain size
        x1 = x0 + coords[2]-1
        y1 = y0 + coords[3]-1
        pattern = pattern_dic[box[4]]
        # Add box to specific layer of grid
        grid[x0:x1,y0:y1,pattern] += 1
    if visualize: visualize_grid(grid)
    common_box = np.argmax(grid,axis=2)
    if visualize: visualize_common_box(common_box)
    if return_all_pattern: return grid
    else: return common_box

    
def find_filename(filenames, string='Aqua_MODIS'):
    for i in range(len(filenames)):
        if string in filenames[i]:
            return filenames[i]

    