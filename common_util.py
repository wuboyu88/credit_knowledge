# -*- coding: utf-8 -*-
import pandas as pd


def delay_status_map(x):
    """
    逾期状态
    :param x: 逾期天数
    :return: 逾期状态
    """
    if pd.isna(x) or x == 0:
        return 'M0'
    elif x <= 30:
        return 'M1'
    elif x <= 60:
        return 'M2'
    elif x <= 90:
        return 'M3'
    elif x <= 120:
        return 'M4'
    elif x <= 150:
        return 'M5'
    elif x <= 180:
        return 'M6'
    else:
        return 'M7及M7+'


def get_one_term_rate(df_one_term, key_name, m_current_name, m_next_name):
    """
    根据一期的逾期信息得到转化率，亦可理解为以当前期月底作为观察点，观察前后一个月的逾期信息得到的滚动率
    :param df_one_term: 一期的逾期信息数据集
    :param key_name: 主键列名
    :param m_current_name: 当前期列名
    :param m_next_name: 下一期列名
    :return result
    """
    # 按照当前月和下一个月两个字段同时进行统计频数(即分子)
    r1 = df_one_term.groupby([m_current_name, m_next_name]).count().reset_index()

    # 当前月每个逾期类型对应客户数(即分母)
    r2 = df_one_term.groupby([m_current_name]).count().reset_index()[[m_current_name, key_name]]

    # 关联r1和r2
    r = pd.merge(r1, r2, on=m_current_name, suffixes=('_numerator', '_denominator'))

    # 计算占比(分子/分母)
    r['ratio'] = r['{}_numerator'.format(key_name)] / r['{}_denominator'.format(key_name)]

    # 生成透视表
    result = pd.pivot_table(r, index=[m_current_name], columns=m_next_name, values='ratio')

    # 缺失值填0
    result.fillna(0, inplace=True)
    return result
