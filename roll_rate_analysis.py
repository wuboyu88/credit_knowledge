# -*- coding: utf-8 -*-
import pandas as pd
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from credit_knowledge.common_util import delay_status_map, get_one_term_rate


def get_roll_rate(loan_repay_detail, key_name, term_name, prin_days_name, accu_days_name, obs_term, nb_months_before=6,
                  nb_months_after=6, status='delay_status'):
    """
    滚动率（每期取算数平均值）
    :param loan_repay_detail: 贷款还款明细表
    :param key_name: 主键列名
    :param term_name: 期数列名
    :param prin_days_name: 本金逾期天数列名
    :param accu_days_name: 利息逾期天数列名
    :param obs_term: 观察点对应的期数, 例如2016-12
    :param nb_months_before: 观察点前的月份数
    :param nb_months_after: 观察点后的月份数
    :param status: delay_status(本息), prin_delay_status(本金), accu_delay_status(利息)
    :return: 滚动率
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

    # 得到观察点前后的月份
    months_before = [(pd.to_datetime(obs_term) - relativedelta(months=nb_months_before - 1 - i)).strftime('%Y-%m') for i
                     in range(nb_months_before)]
    months_after = [(pd.to_datetime(obs_term) + relativedelta(months=i + 1)).strftime('%Y-%m') for i in
                    range(nb_months_after)]

    # 得到观察点前后对应的数据集
    df_before = df_loan[df_loan[term_name].isin(months_before)]
    df_after = df_loan[df_loan[term_name].isin(months_after)]

    # 每个客户观察点前的最严重逾期状态
    r_before = df_before.groupby(key_name)[status].max().reset_index()

    # 每个客户观察点后的最严重逾期状态
    r_after = df_after.groupby(key_name)[status].max().reset_index()

    r = pd.merge(r_before, r_after, on=[key_name], suffixes=('_current', '_next'))

    m_current_name = status + '_current'
    m_next_name = status + '_next'
    result = get_one_term_rate(r, key_name, m_current_name, m_next_name)

    return result
