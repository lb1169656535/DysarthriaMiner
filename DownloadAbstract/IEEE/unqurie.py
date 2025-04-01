import pandas as pd

# 读取CSV文件
df = pd.read_csv("p.csv")

# 检查摘要重复项
duplicates = df[df.abstract.duplicated(keep=False)].sort_values('abstract')

if not duplicates.empty:
    print(f"发现 {len(duplicates)} 条重复摘要：")
    print(duplicates[['id', 'title', 'abstract']])
    
    # 生成带标记的新文件
    df['是否重复'] = df.abstract.duplicated(keep='first').map({True: '是', False: '否'})
    df.to_csv("p_with_duplicates_flag.csv", index=False)
    print("已生成带重复标记的文件：papers_with_duplicates_flag.csv")
else:
    print("未发现重复摘要")
