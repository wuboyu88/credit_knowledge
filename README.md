# 信贷业务知识

## 滚动率 & 迁移率 & 账龄

**代码示例:**
```python
import pandas as pd
from credit_knowledge.roll_rate_analysis import get_roll_rate
from credit_knowledge.flow_rate_analysis import get_flow_rate
from credit_knowledge.vintage_analysis import get_vintage, vintage_to_excel

loan_repay_detail = pd.read_csv('credit_knowledge/example/data/loan_repay_detail.csv')

key_name = 'loan_no'
term_name = 'term'
loan_date_name = 'loan_date'
prin_days_name = 'prin_days'
accu_days_name = 'accu_days'

# 滚动率
df_roll_rate = get_roll_rate(loan_repay_detail, key_name, term_name, prin_days_name, accu_days_name, obs_term='2020-06',
                             nb_months_before=6, nb_months_after=6, status='delay_status')

# 迁移率
df_flow_rate = get_flow_rate(loan_repay_detail, key_name, term_name, prin_days_name, accu_days_name,
                             status='delay_status')

# 账龄
df_vintage = get_vintage(loan_repay_detail, key_name, loan_date_name, term_name, prin_days_name, accu_days_name,
                         nb_mob=12, overdue_days_threshold=30, dimension='loan')

# 账龄写入excel
vintage_to_excel(df_vintage, 'credit_knowledge/example/vintage_analysis.xlsx', nb_month_per_graph=12)
```

## References
https://zhuanlan.zhihu.com/p/81027037/

## License
[MIT](https://choosealicense.com/licenses/mit/)