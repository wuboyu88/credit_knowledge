# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from copy import deepcopy
import re


def get_mob_bad_rate(x, mob, key_name):
    """
    计算每个mob对应的逾期率
    :param x: 数据集
    :param mob: 账龄
    :param key_name: 主键列名
    :return: 逾期率
    """
    return x[(x['GOOD_BAD_FLAG'] == 1) & (x['MOB'] <= mob)][key_name].nunique() / x[key_name].nunique()


def get_vintage(loan_repay_detail, key_name, loan_date_name, term_name, prin_days_name, accu_days_name, nb_mob=36,
                overdue_days_threshold=30, dimension='loan'):
    """
    账龄分析表
    :param loan_repay_detail: 贷款还款明细表
    :param key_name: 主键列名
    :param loan_date_name: 放款日期列名
    :param term_name: 期数列名
    :param prin_days_name: 本金逾期天数列名
    :param accu_days_name: 利息逾期天数列名
    :param nb_mob: mob的个数, 默认是36
    :param overdue_days_threshold: 好坏标志对应的逾期天数阀值, 默认是30, 一般是通过滚动率或迁移率确定, 比如认为M1是坏则对应30天
    :param dimension: 统计维度, 默认是借据号维度loan, 也可以是客户号维度customer
    :return: 账龄分析表
    """
    if dimension == 'customer':
        # 同一个客户同一期数取逾期天数的最大值
        df_left = loan_repay_detail.groupby([key_name, term_name]).agg(
            {prin_days_name: 'max', accu_days_name: 'max'}).reset_index()
        # 同一个客户取最早的放款日期
        df_right = loan_repay_detail.groupby([key_name]).agg({loan_date_name: 'min'}).reset_index()
        df_loan = pd.merge(df_left, df_right, on=key_name)
    else:
        df_loan = deepcopy(loan_repay_detail)

    # 放款日期作为首期
    df_loan['FIRST_TERM'] = df_loan[loan_date_name]

    # 本息逾期天数最大值
    df_loan['MAX_DELAY_DAYS'] = df_loan[[prin_days_name, accu_days_name]].max(axis=1)

    # MOB为TERM和FIRST_TERM的月份差
    df_loan['MOB'] = np.round(
        (pd.to_datetime(df_loan[term_name]) - pd.to_datetime(df_loan['FIRST_TERM'])) / np.timedelta64(1, 'M'))

    # 好坏标志（根据滚动率或迁移率判断）
    df_loan['GOOD_BAD_FLAG'] = df_loan['MAX_DELAY_DAYS'].apply(lambda x: 1 if x > overdue_days_threshold else 0)

    # 账龄分析表
    df_vintage = pd.DataFrame(index=sorted(df_loan['FIRST_TERM'].unique()))
    df_vintage.index.rename('FIRST_TERM', inplace=True)

    for i in range(1, nb_mob + 1):
        df_vintage.loc[:, 'MOB{}_BAD_RATE'.format(i)] = df_loan.groupby('FIRST_TERM').apply(
            lambda x: get_mob_bad_rate(x, i, key_name))

    df_vintage.reset_index(inplace=True)
    return df_vintage


def vintage_to_excel(df_vintage, output_file_path, nb_month_per_graph=12):
    """
    将df_vintage写到excel中并画出折线图
    :param df_vintage: 账龄分析表
    :param output_file_path: excel文件路径
    :param nb_month_per_graph: 每张图片最多显示的月份数
    :return: None
    """
    df = deepcopy(df_vintage)
    categories = df['FIRST_TERM'].tolist()
    df.set_index('FIRST_TERM', inplace=True)
    df.columns = [int(re.findall(r'.*?(\d+).*', ele)[0]) for ele in df.columns]
    df = df.T
    max_row = len(df)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    sheet_name = 'Sheet1'
    writer = pd.ExcelWriter(output_file_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name)

    # Access the XlsxWriter workbook and worksheet objects from the dataframe.
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    for j in range(0, len(categories), nb_month_per_graph):
        chart = workbook.add_chart({'type': 'line'})

        for i in range(j, min(j + nb_month_per_graph, len(categories))):
            col = i + 1
            chart.add_series({
                'name': [sheet_name, 0, col],
                'categories': [sheet_name, 1, 0, max_row, 0],
                'values': [sheet_name, 1, col, max_row, col],
            })

        chart.set_x_axis({'name': 'MOB'})
        chart.set_y_axis({'name': 'OVERDUE_RATE'})

        worksheet.insert_chart(1 + int(20 * j / nb_month_per_graph), df.shape[1] + 2, chart,
                               {'x_scale': 1, 'y_scale': 1.3})

    writer.save()
