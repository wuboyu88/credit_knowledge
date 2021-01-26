import pandas as pd


def get_one_term_rate(df_one_term, key_name, m_current_name, m_next_name):
    """
    根据一期的逾期信息得到转化率，亦可理解为以当前期月底作为观察点，观察前后一个月的逾期信息得到的滚动率
    :param df_one_term: 一期的逾期信息数据表
    :param key_name: 主键列名
    :param m_current_name: 当前期列名
    :param m_next_name: 下一期列名
    :return: result
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


def get_flow_rate(df_overdue, term_name, key_name, m_current_name, m_next_name):
    """
    得到迁移率（每期取算数平均值）
    :param df_overdue: 逾期期数数据集
    :param term_name: 期数列名
    :param key_name: 主键列名
    :param m_current_name: 当前期列名
    :param m_next_name: 下一期列名
    :return: result
    """
    term_list = sorted(list(df_overdue[term_name].unique()))
    result = None
    for term in term_list:
        df_one_term = df_overdue[df_overdue[term_name] == term]
        one_term_result = get_one_term_rate(df_one_term, key_name, m_current_name, m_next_name)
        if result is None:
            result = one_term_result
        else:
            result = result.add(one_term_result, fill_value=0)
    result = result / len(term_list)
    return result


if __name__ == '__main__':
    df = pd.read_csv('data/overdue.csv')
    flow_rate = get_flow_rate(df, 'term', 'cust_num', 'm_current', 'm_next')
