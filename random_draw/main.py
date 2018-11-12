#!/usr/bin/python3

import sys
import random

# 接受传入参数
draw_user_file_path = sys.argv[1]
prize_num = sys.argv[2]

# 读取参与者邮箱列表文件
r = open(draw_user_file_path, 'r')
user_list = r.readlines()
r.close()

# 打印参与者列表
print('参与奖品编号为：' + str(prize_num) + ' 的抽奖参与者邮箱列表：')
print('-' * 20)
for i in user_list:
    print('参与者：' + '****' + i[3:].strip('\n'))
print('-' * 20 + '\n' * 2)

# 抽奖开始
print('抽奖开始！')
print('-' * 20)
i = 0
while i < 3:
    lucky_user = random.choice(user_list)
    user_list_input = user_list.remove(lucky_user)

    if i == 0:
        print('中奖者为：' + '****' + lucky_user[3:-1])
    elif i == 1:
        print('候选中奖者1为：' + '****' + lucky_user[3:-1])
    else:
        print('候选中奖者2为：' + '****' + lucky_user[3:-1])
    i += 1
print('-' * 20)
print('抽奖结束！' + '\n' * 2)
