# coding: utf-8

input_file = "/data/dictionary.txt"   # 你的词典文件路径
output_file = "insert_sign_word.sql"

# 示例：如果你已经有动作说明和中文释义，建议用dict补全，否则先生成基础SQL
default_action_desc = ''
default_chinese_meaning = ''

with open(input_file, encoding="utf-8") as fin, open(output_file, "w", encoding="utf-8") as fout:
    for line in fin:
        line = line.strip()
        if not line: continue
        parts = line.split('\t')
        if len(parts) != 2:
            continue
        idx, word = parts
        # 视频路径补全为6位编号
        idx_str = idx.zfill(6)
        video_url = f"http://localhost:8000/ptov/{idx_str}.mp4"
        # SQL 语句，注意转义
        sql = f"INSERT INTO sign_word (word, video_url, action_desc, chinese_meaning) VALUES ('{word}', '{video_url}', '{default_action_desc}', '{default_chinese_meaning}');\n"
        fout.write(sql)

print("批量插入SQL已生成到 insert_sign_word.sql")
