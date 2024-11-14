# This file contains the main functions to run the experiments (E1-E4) for the IDSD paper.

from subgroups.algorithms.subgroup_sets.idsd import IDSD
from subgroups.algorithms.subgroup_sets.bsd import BSD
from subgroups.algorithms.subgroup_sets.qfinder import QFinder
from subgroups.algorithms.subgroup_sets.sdmapstar import SDMapStar
from subgroups.algorithms.subgroup_sets.vlsd import VLSD
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.wracc_optimistic_estimate_1 import WRAccOptimisticEstimate1


from pandas import DataFrame,read_csv, Series, concat
import os
import time
import random 
import psutil
from sklearn.model_selection import train_test_split, StratifiedKFold

quality_models = ["BSD","SDMapStar","VLSD"]


def get_model(model, write,database = None, k = 10):
    id = random.randint(0, 100000)
    if database is not None:
        if model == "SDMapStar":
            if database == "MIMIC":
                thresh = .01
                min_n = 100
            elif database == "Mushrooms":
                thresh = .15
                min_n = 100
            elif database == "AB":
                thresh = -1
                min_n = 0
            else:
                print("WARNING: LIMIT NOT TESTED")
                thresh = 0
                min_n = 0
        elif model == "VLSD":
            thresh = 0.01
        
    if model == "IDSD":
        return IDSD(num_subgroups=k, max_complexity=5, write_results_in_file=write, file_path=f"results_IDSD_{id}.txt"), id
    elif model == "BSD":
        return BSD(quality_measure=WRAcc(), optimistic_estimate=WRAccOptimisticEstimate1(), min_support=0, num_subgroups=k, max_depth=5, write_results_in_file=write, file_path=f"results_BSD_{id}.txt"), id
    elif model == "QFinder":
        return QFinder(num_subgroups=k, max_complexity=5, write_results_in_file=write, file_path=f"results_QFinder_{id}.txt"), id
    elif model == "SDMapStar":
        if write:
            return SDMapStar(quality_measure=WRAcc(), optimistic_estimate=WRAccOptimisticEstimate1(),minimum_quality_measure_value = thresh, minimum_n=min_n, num_subgroups=k, write_results_in_file=True, file_path=f"results_SDMapStar_{id}.txt"), id
        else:
            return SDMapStar(quality_measure=WRAcc(), optimistic_estimate=WRAccOptimisticEstimate1(),minimum_quality_measure_value = -2, minimum_n=0, num_subgroups=k, write_results_in_file=False), id
    elif model == "VLSD":
        if write:
            return VLSD(quality_measure=WRAcc(), optimistic_estimate=WRAccOptimisticEstimate1(), q_minimum_threshold=thresh, oe_minimum_threshold=thresh, write_results_in_file=True, file_path=f"results_VLSD_{id}.txt"), id
        else:
            return VLSD(quality_measure=WRAcc(), optimistic_estimate=WRAccOptimisticEstimate1(), q_minimum_threshold=-2, oe_minimum_threshold=-2, write_results_in_file=False), id
    else:
        raise ValueError("Model not recognized")

def get_data(database:str,instances:int = None, split:bool = False):
    if database == "MIMIC":
        return get_mimic_data(split)
    elif database == "Mushrooms":
        return get_mushrooms_data(split, instances)
    elif database == "AB":
        return get_ab(split, instances)
    elif database == "Car":
        return get_car_data(split)
    else:
        raise ValueError("Database not recognized")
    
def get_folds(dataframe: DataFrame, target:tuple ,k:int = 10):
    skf = StratifiedKFold(n_splits=k, random_state=42, shuffle=True)
    folds = []
    for train_index, test_index in skf.split(dataframe, dataframe[target[0]]):
        train = dataframe.iloc[train_index]
        test = dataframe.iloc[test_index]
        folds.append((train, test))
    return folds

def get_mimic_data(split:bool):
    if split:
        df_train = read_csv('../data/mimic-iii-train.csv')
        df_test = read_csv('../data/mimic-iii-test.csv')
        df_train = df_train.astype("str")
        df_train.columns = df_train.columns.astype(str)
        df_test = df_test.astype("str")
        df_test.columns = df_test.columns.astype(str)
        return df_train, df_test
    df = read_csv('../data/mimic-iii.csv')
    df = df.astype("str")
    df.columns = df.columns.astype(str)
    return df

def get_mushrooms_data(split:bool, instances:int = None):
    if split:
        # df_train = read_csv('../data/agaricus-lepiota-train.csv', header = None)
        # df_test = read_csv('../data/agaricus-lepiota-test.csv', header = None)
        df_train = read_csv('../data/agaricus-lepiota-train.csv')
        df_test = read_csv('../data/agaricus-lepiota-test.csv')
        df_train = df_train.astype("str")
        df_train.columns = [ "poisonous",
        "cap-shape", "cap-surface", "cap-color", "bruises", "odor",
        "gill-attachment", "gill-spacing", "gill-size", "gill-color",
        "stalk-shape", "stalk-root", "stalk-surface-above-ring",
        "stalk-surface-below-ring", "stalk-color-above-ring",
        "stalk-color-below-ring", "veil-type", "veil-color",
        "ring-number", "ring-type", "spore-print-color",
        "population", "habitat"]
        df_test = df_test.astype("str")
        df_test.columns = df_train.columns
        return df_train, df_test
    if instances is not None:
        df = read_csv(f'../data/agaricus-lepiota-sample-{instances}.csv', header = None)
    else:
        df = read_csv('../data/agaricus-lepiota.data', header = None)
    df.columns = [ "poisonous",
        "cap-shape", "cap-surface", "cap-color", "bruises", "odor",
        "gill-attachment", "gill-spacing", "gill-size", "gill-color",
        "stalk-shape", "stalk-root", "stalk-surface-above-ring",
        "stalk-surface-below-ring", "stalk-color-above-ring",
        "stalk-color-below-ring", "veil-type", "veil-color",
        "ring-number", "ring-type", "spore-print-color",
        "population", "habitat"]
    df = df.astype("str")
    return df

def get_car_data(split:bool):
    if split:
        df_train = read_csv('../data/car-train.csv', header = None)
        df_test = read_csv('../data/car-test.csv', header = None)
        df_train = df_train.astype("str")
        df_train.columns = ["buying", "maint", "doors", "persons", "lug_boot", "safety", "acceptability"]
        df_test = df_test.astype("str")
        df_test.columns = df_train.columns
        return df_train, df_test
    df = read_csv('../data/car.data', header = None)
    df.columns = ["buying", "maint", "doors", "persons", "lug_boot", "safety", "acceptability"]
    df = df.astype("str")
    return df

def get_ab(split: bool = False, instances:int = 400):
    if instances is None:
        instances = 400
    df = read_csv(f'../data/mimic-iii-preprocessed-db-sample-{instances}.csv')
    df = df.astype("str")
    df.columns = df.columns.astype(str)
    cols = df.columns.to_list()
    cols.remove("culture_susceptibility")
    cols.insert(0, "culture_susceptibility")
    df = df[cols]
    if not split:
        return df
    # stratified split
    df_train, df_test = train_test_split(df, test_size=0.2, stratify=df["culture_susceptibility"], random_state=42)
    return df_train, df_test

def get_target(database:str):
    if database == "MIMIC":
        return ("interpretation", "R")
    elif database == "Mushrooms":
        return ("poisonous", "e")
    elif database == "AB":
        return ("culture_susceptibility", "R")
    elif database == "Car":
        return ("acceptability", "unacc")
    else:
        raise ValueError("Database not recognized")
    
def output_csv(model, id, df = None, target = None, num_subgroup = None):
    input_file = f"results_{model}_{id}.txt"
    is_quality = model in quality_models
    if not is_quality and (df is None or target is None):
        raise ValueError("Need to pass df if model is not quality based")
    if is_quality:
        output_df = DataFrame(columns=["Description","Quality","tp","fp", "TP","FP"])
    else:
        output_df = DataFrame(columns=["Description","tp","fp", "TP","FP"])
        target_entry = df[target[0]] == target[1]
    try:
        # print(input_file)
        f = open(input_file, "r")
    except Exception:
        print(f"WARNING: No results found for {model} with id {id}")
        return output_df
    for line in f:
        description_str = line.split("Description: [")[1].split("], Target:")[0]
        if is_quality:
            quality = float(line.split("Quality Measure WRAcc = ")[1].split(" ;")[0])
            tp = int(line.split("tp = ")[1].split(" ;")[0])
            fp = int(line.split("fp = ")[1].split(" ;")[0])
            TP = int(line.split("TP = ")[1].split(" ;")[0])
            FP = int(line.split("FP = ")[1].split(" ;")[0])
            output_df.loc[len(output_df)] = [description_str, quality, tp, fp, TP, FP]
        else:
            entry = Series(True, index=df.index)
            for selector in description_str.split(", "):
                column = selector.split(" = ")[0]
                value = selector.split(" = ")[1]
                value = value.replace("'", "")
                entry = entry & (df[column] == value)
            tp = sum(entry & target_entry)
            fp = sum(entry & ~target_entry)
            TP = sum(target_entry)
            FP = len(target_entry) - TP
            output_df.loc[len(output_df)] = [description_str, tp, fp, TP, FP]
    os.remove(input_file)
    if num_subgroups is not None and "Quality" in output_df.columns:
        output_df.sort_values(by="Quality", ascending=False, inplace=True)
        output_df = output_df.iloc[0:num_subgroups]
    f.close()
    return output_df
    
def output_csv_test(train_output, df_test, target, num_subgroups:int = None):
    output_df = train_output.copy()
    target_entry = df_test[target[0]] == target[1]
    for i in range(len(output_df)):
        description_str = output_df.iloc[i]
        description_str = description_str.Description
        entry = Series(True, index=df_test.index)
        for selector in description_str.split(", "):
            column = selector.split(" = ")[0]
            value = selector.split(" = ")[1]
            value = value.replace("'", "")
            entry = entry & (df_test[column] == value)
        tp = sum(entry & target_entry)
        fp = sum(entry & ~target_entry)
        TP = sum(target_entry)
        FP = len(target_entry) - TP
        output_df.loc[output_df.index[i], "tp test"] = tp
        output_df.loc[output_df.index[i], "fp test"] = fp
        output_df.loc[output_df.index[i], "TP test"] = TP
        output_df.loc[output_df.index[i], "FP test"] = FP
    output_df.rename(columns={"tp":"tp train","fp":"fp train","TP":"TP train","FP":"FP train"}, inplace=True)
    return output_df


def benchmark(model, database, columns:int = None, instances = None):
    if columns is not None and columns < 5:
        raise ValueError("Columns must be at least 5")
    if instances is not None:
        df = get_data(database, split = False, instances=instances)
    else:
        df = get_data(database, split= False)
    if columns is not None:
        df = df.iloc[:,0:columns+1] # +1 for target
    target = get_target(database)
    model, id = get_model(model, False)
    t0 = time.process_time()
    model.fit(df, target)
    t1 = time.process_time()
    p = psutil.Process()
    mem = p.memory_info().rss
    return t1-t0, mem

def run(model, database, split, num_subgroups:int = 10):
    if split:
        df_train, df_test = get_data(database, split = True)
        target = get_target(database)
        sd, id = get_model(model, write = True, database=database, k=num_subgroups)
        sd.fit(df_train, target)
        output_train = output_csv(model, id, df_train, target, num_subgroups)
        output_test = output_csv_test(output_train, df_test, target)
        return output_test
    else:
        df = get_data(database, split = False)
        target = get_target(database)
        sd, id = get_model(model, write = True, database=database, k=num_subgroups)
        sd.fit(df, target)
        return output_csv(model, id, df, target, num_subgroups)
    
def run_cross_validation(model, database, num_subgroups:int = 10):
    df = get_data(database, split = False)
    target = get_target(database)
    folds = get_folds(df,target)
    output_df = DataFrame()
    for i in range(len(folds)):
        train, test = folds[i]
        sd, id = get_model(model, write = True, database=database)
        sd.fit(train, target)
        output_train = output_csv(model, id, train, target, num_subgroups)
        output_test = output_csv_test(output_train, test, target)
        output_df = concat([output_df, output_test])
    return output_df

if len(sys.argv) < 2:
    raise ValueError("Need to pass mode")
print(sys.argv)
mode = sys.argv[1]
if mode == "benchmark":
    if len(sys.argv) < 5:
        raise ValueError("Usage: benchmark model database [instances n] [columns n]")
    model = sys.argv[2]
    database = sys.argv[3]
    instances = None
    columns = None
    if "instances" in sys.argv:
        idx = sys.argv.index("instances")
        instances = sys.argv[idx+1]
        instances = int(instances)
    if "columns" in sys.argv:
        idx = sys.argv.index("columns")
        columns = sys.argv[idx+1]
        columns = int(columns)
    print(benchmark(model,database,columns=columns,instances=instances))
elif mode == "run":
    if len(sys.argv) < 5:
        raise ValueError("Usage: run model database split [num_subgroups]")
    model = sys.argv[2]
    database = sys.argv[3]
    split = sys.argv[4]
    split = split == "True"
    if len(sys.argv) > 5:
        try:
            num_subgroups = int(sys.argv[5])
        except Exception:
            raise ValueError("num_subgroups must be an integer")
    else:
        num_subgroups = 10
    output_df = run(model,database,split,num_subgroups)
    output_df.to_csv(f"results_{model}_{database}.csv")
elif mode == "cross_validation":
    if len(sys.argv) < 4:
        raise ValueError("Usage: cross_validation model database [num_subgroups]")
    model = sys.argv[2]
    database = sys.argv[3]
    if len(sys.argv) > 4:
        num_subgroups = sys.argv[4]
    else:
        num_subgroups = 10
    output_df = run_cross_validation(model,database,num_subgroups)
    output_df.to_csv(f"results_{model}_{database}_cross_validation.csv")