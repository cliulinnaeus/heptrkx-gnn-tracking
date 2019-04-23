#!/usr/bin/env python3

def read_pairs(pairs_path):
    with pd.HDFStore(pairs_path) as store:
        try:
            df_input = store['data']
        except KeyError:
            print(pairs_path)
            return None

    return df_input


def process(pair_idx, evt_id_list, output_dir):
    pair_name = 'pair{:03d}.h5'.format(pair_idx)
    out_name = os.path.join(output_dir, pair_name)
    if os.path.exists(out_name):
        print(out_name, "is there")
        return

    pairs_list = [read_pairs(os.path.join(x, pair_name)) for x in evt_id_list]
    pairs_list = [x for x in pairs_list if x is not None]
    if len(pairs_list) > 0:
        out_df = pd.concat(pairs_list, ignore_index=True)
        with pd.HDFStore(out_name) as store:
            store['data'] = out_df
    else:
        print(pair_name)


if __name__ == "__main__":
    import os
    import sys
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(description="merge true pairs")
    add_arg = parser.add_argument
    add_arg('pairs_dir', nargs='?', default='/global/cscratch1/sd/xju/heptrkx/pairs/true_pairs')
    add_arg('output_dir', nargs='?', default='/global/cscratch1/sd/xju/heptrkx/pairs/merged_true_pairs')

    args = parser.parse_args()
    path = args.pairs_dir
    output_dir = args.output_dir

    import glob
    evt_ids = glob.glob(os.path.join(path, '*'))
    #evt_ids = [int(os.path.basename(x)[3:]) for x in dir_names]
    n_total = len(evt_ids)
    print("Total events:", len(evt_ids))
    print("80% for training, 10% for validation and 10% for testing")

    tr_dir_name = 'training'
    val_dir_name = 'validation'
    test_dir_name = 'testing'
    os.makedirs(os.path.join(output_dir, tr_dir_name), exist_ok=True)
    os.makedirs(os.path.join(output_dir, val_dir_name), exist_ok=True)
    os.makedirs(os.path.join(output_dir, test_dir_name), exist_ok=True)

    from nx_graph.utils_data import split_list
    evt_ids_tr, evt_ids_val, evt_ids_test = split_list(evt_ids)
    print("Training:",   len(evt_ids_tr))
    print("Validation:", len(evt_ids_val))
    print("Testing:", len(evt_ids_test))

    import pandas as pd

    from make_true_pairs_for_training_segments import layer_pairs

    from functools import partial
    import multiprocessing as mp

    pp_layers_info = list(range(len(layer_pairs)))
    n_workers = int(os.getenv('SLURM_CPUS_PER_TASK'))
    print("# workers:", n_workers)
    print(evt_ids_tr[0])
    print(pp_layers_info[0])

    with mp.Pool(processes=n_workers) as pool:
        pp_func = partial(process, evt_id_list=evt_ids_tr, output_dir=os.path.join(output_dir, tr_dir_name))
        pool.map(pp_func, pp_layers_info)

    with mp.Pool(processes=n_workers) as pool:
        pp_func = partial(process, evt_id_list=evt_ids_val, output_dir=os.path.join(output_dir, val_dir_name))
        pool.map(pp_func, pp_layers_info)

    with mp.Pool(processes=n_workers) as pool:
        pp_func = partial(process, evt_id_list=evt_ids_test, output_dir=os.path.join(output_dir, test_dir_name))
        pool.map(pp_func, pp_layers_info)
