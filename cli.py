# -*- coding: utf-8 -*-
import argparse
import json
import sys
import warnings
warnings.simplefilter("ignore")

# default vars decided by business group
default_min_qc_score = 5
default_coefficient = 0.005


def create_parser(args):
    # default vars decided by business group
    parser = argparse.ArgumentParser(description='Calculating star rating for teachers using QC and behavior data.')
    subparsers = parser.add_subparsers(help="Use the different mode,'normal', 'FAM' or 'FAM_airflow'")
    # normal mode parser
    parser_normal_mode = subparsers.add_parser("normal", help="normal_mode")
    parser_normal_mode.add_argument('mode', type=str, help='with_total_score or origin')
    parser_normal_mode.add_argument('teacher_star_data', type=str, help='Teacher star data json file path')
    parser_normal_mode.add_argument('star_rate_data', type=str, help='Path to star_rate standard data json file')
    parser_normal_mode.add_argument(
        '--output', type=str, default=sys.stdout,
        help='Output data. The standard output is default.'
    )
    parser_normal_mode.add_argument(
        '--min_qc_scores', type=int, default=5,
        help="Minimum count of QC scores for each teacher [{}]".format(default_min_qc_score)
    )
    parser_normal_mode.add_argument(
        '--coefficient', type=float, default=0.005,
        help="Standardize the QC scores for calculating the total scores [{}]".format(default_coefficient)
    )
    # FAM mode parser
    parser_fam_mode = subparsers.add_parser("FAM", help="FAM_mode, use the FAM to process data")
    parser_fam_mode.add_argument('data_path', type=str, help='Six data of teacher star data, including star rate')
    parser_fam_mode.add_argument(
        '--output', type=str, default=sys.stdout,
        help='Output data. The standard output is default. With FA_Model, please use the csv format'
    )
    # FAM mode, airflow deploy ready version
    parser_fam_airflow = subparsers.add_parser("FAM_airflow", help="FAM_mode, airflow deploy ready")
    # 传入两个json文件路径，读取其中的参数
    parser_fam_airflow.add_argument('conn_info', type=str,
                                    help='Path of a json file contains conn_info of the databases')
    parser_fam_airflow.add_argument('teacher_star_vars', type=str, help='Path of an json object contains data path')

    return parser.parse_args(args)


def data_processing(mode, teacher_star_data, star_rate_data, output=sys.stdout, min_qc_score=default_min_qc_score, coefficient=default_coefficient):
    with open(teacher_star_data) as file:
        total_score = json.load(file)["data"]
    with open(star_rate_data) as file:
        star_rate = json.load(file)

    if mode == "origin":
        total_score = LastFiveQcScore.call_control_funcs(total_score, min_qc_score, coefficient)
    elif mode == "with_total_score":
        pass
    else:
        raise Exception("Invalid mode!", mode)

    teacher_star_object = AwjTeacherStarSnapshot(total_score, star_rate, min_qc_score, coefficient)
    sorted_total_score_list = teacher_star_object.get_total_score_list()
    cal_star_rate_list = teacher_star_object.cal_star_rate_min_score(sorted_total_score_list)
    total_teacher_star_data = teacher_star_object.total_teacher_star(cal_star_rate_list)
    if output == sys.stdout:
        json.dump(total_teacher_star_data, sys.stdout)
    else:
        with open(output, "w", encoding="utf-8") as file:
            json.dump(total_teacher_star_data, file)

    return 0


def use_fa_model(path, output=sys.stdout):
    pre_proc_obj = FAModelDataPreProc(path)
    df_wide_proc = pre_proc_obj.gen_df_wide_final()
    fa_main_obj = FAModelMain(df_wide_proc)
    df_wide, df_wide_final = fa_main_obj.fix_process_final()
    with open(path + "star_rate.json") as file:
        star_rate = json.load(file)
    config_obj = ConfigurationsFAM()
    fa_indexs = config_obj.get_fa_indexs()
    gen_ts_obj = GenTeacherStar(star_rate, fa_indexs, df_wide, df_wide_final)
    data_processed_with_fam = gen_ts_obj.gen_final_table()
    # to_json直接sys.stdout输出
    if output == sys.stdout:
        data_processed_with_fam.to_json(sys.stdout)
    else:
        data_processed_with_fam.to_csv(output, encoding="utf-8", index=False, float_format='%.5f')

    return 0


def auto_fam_with_sql(conn_info, teacher_star_vars):
    # 读取两个配置文件
    with open(conn_info) as file:
        data_conn = json.load(file)
    with open(teacher_star_vars) as file:
        data_vars = json.load(file)
    auto_fam_obj = AutomaticFAM(data_conn, data_vars)
    auto_fam_obj.gen_data_sets()
    auto_fam_obj.auto_fa_model()

    return 0


def main(argv=sys.argv[1:]):
    args = create_parser(argv)

    # 如果什么都没有输入加入异常处理
    if len(argv) > 0:
        if argv[0] == "normal":
            data_processing(
                args.mode, args.teacher_star_data, args.star_rate_data,
                args.output, args.min_qc_scores, args.coefficient
            )
        elif argv[0] == "FAM":
            use_fa_model(args.data_path, args.output)
        elif argv[0] == "FAM_airflow":
            auto_fam_with_sql(args.conn_info, args.teacher_star_vars)
    else:
        raise ValueError("Please check your input with the help information or the readme file")

    return 0
