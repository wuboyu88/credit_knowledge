# -*- coding: utf-8 -*-
import pandas as pd
from copy import deepcopy
from credit_knowledge.common_util import delay_status_map, get_one_term_rate


def get_flow_rate(loan_repay_detail, key_name, term_name, prin_days_name, accu_days_name, status='delay_status'):
    """
    迁移率（每期取算数平均值）
    :param loan_repay_detail: 贷款还款明细表
    :param key_name: 主键列名
    :param term_name: 期数列名
    :param prin_days_name: 本金逾期天数列名
    :param accu_days_name: 利息逾期天数列名
    :param status: delay_status(本息), prin_delay_status(本金), accu_delay_status(利息)
    :return: 迁移率
    """
    df_loan = deepcopy(loan_repay_detail)

    # 本息逾期天数最大值
    df_loan['MAX_DELAY_DAYS'] = df_loan[[prin_days_name, accu_days_name]].max(axis=1)

    if status == 'prin_delay_status':
        df_loan[status] = df_loan[prin_days_name].apply(delay_status_map)
    elif status == 'accu_delay_status':
        df_loan[status] = df_loan[accu_days_name].apply(delay_status_map)
    else:
        df_loan[status] = df_loan['MAX_DELAY_DAYS'].apply(delay_status_map)

    # 字符串yyyy-mm转成数值型yyyymm
    df_loan[term_name] = df_loan[term_name].apply(lambda x: int(x[0:4]+x[5:7]))

    # 当前期
    df_current = deepcopy(df_loan)
    df_current['rank'] = df_current.groupby([key_name])[term_name].rank(method='first')

    # 下一期
    df_next = deepcopy(df_loan)
    df_next['rank'] = df_next.groupby([key_name])[term_name].rank(method='first')-1
    df_next = df_next[[key_name, status, 'rank']]

    df_all = pd.merge(df_current, df_next, on=[key_name, 'rank'], suffixes=('_current', '_next'))

    term_list = sorted(list(df_all[term_name].unique()))
    result = None
    for term in term_list:
        df_one_term = df_all[df_all[term_name] == term]
        one_term_result = get_one_term_rate(df_one_term, key_name, status + '_current', status + '_next')
        if result is None:
            result = one_term_result
        else:
            result = result.add(one_term_result, fill_value=0)
    result = result / len(term_list)
    return result
