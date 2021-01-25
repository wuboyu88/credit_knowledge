# 信贷业务知识

## 1.迁移率

**代码示例:**
```python
import pandas as pd
from flow_rate_analysis import get_flow_rate
df = pd.read_csv('data/overdue.csv')
flow_rate = get_flow_rate(df, 'term', 'cust_num', 'm_current', 'm_next')
```

**运行结果:**
```
m_next           M0        M1        M2
m_current                              
M0         0.500000  0.000000  0.500000
M1         0.333333  0.000000  0.666667
M2         0.833333  0.166667  0.000000
```

## References
https://zhuanlan.zhihu.com/p/81027037/

## License
[MIT](https://choosealicense.com/licenses/mit/)