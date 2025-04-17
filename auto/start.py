import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime, timedelta
import json
from ruamel.yaml import YAML
import shutil
import os
import requests

def start_chrome_instance(port, user_dir): # 修改，如果浏览器已打开，则无需操作
    # 新增的实例检查逻辑
    try:
        # 尝试访问Chrome调试接口
        debug_url = f"http://localhost:{port}/json/version"
        response = requests.get(debug_url, timeout=0.5)
        
        # 如果响应包含浏览器信息，则说明实例已存在
        if response.status_code == 200 and "Browser" in response.text:
            print(f"port:{port}\t跳过启动")
            return
    except (requests.ConnectionError, requests.Timeout):
        pass
    except Exception as e:
        print(f"⚠️ 实例检查异常: {str(e)}")

    # 原有的启动逻辑
    command = [
        "start",
        "chrome",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_dir}"
    ]
    subprocess.Popen(command, shell=True)


def generate_yaml(nums,target_date=(datetime.now() + timedelta(days=3)), target_time=[22, 0, 0]):
    # 生成日期（当前日期 +3 天）
    target_date = datetime.now() + timedelta(days=3)
    formatted_date = [target_date.year, target_date.month, target_date.day]

    # 构建 accounts 结构
    accounts = []
    for _ in range(nums):
        account = {
            "token": "",
            "court_1": "10",
            "time_1": "20",
            "court_2": "10",
            "time_2": "21"
        }
        accounts.append(account)

    # 构建完整数据结构
    data = {
        "accounts": accounts,
        "config": {
            "venueTypeId": "99f5f83b-2adc-41b6-8c98-901ced354551",
            "date": formatted_date,
            "target_time": target_time,
            "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
    }
    with open("accounts.yaml", "w", encoding="utf-8") as f:
        # 添加文件头注释
        f.write("# accounts.yaml\n")
        
        # 使用 ruamel.yaml 保留格式（需安装：pip install ruamel.yaml）
        # 下面是使用标准库的写法（注释无法保留）
        yaml = YAML()
        yaml.indent(sequence=4, offset=2)
        yaml.dump(
            data,
            f,
            # allow_unicode=True,
            # sort_keys=False,
            # default_flow_style=None,
            # indent=2
        )

def update_token(tokens):
    """更新 YAML 文件的 token 字段并保留原有内容"""
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)  # 保持缩进格式
    
    # 读取现有 YAML 文件
    with open("accounts.yaml", 'r', encoding='utf-8') as f:
        data = yaml.load(f)
    
    # 检查数据合法性
    accounts = data.get('accounts', [])
    if len(accounts) != len(tokens):
        raise ValueError(f"Tokens数量 ({len(tokens)}) 与 accounts数量 ({len(accounts)}) 不匹配")
    
    # 按顺序填充 token
    for account, token in zip(accounts, tokens):
        account['token'] = token
    
    # 写回文件
    with open("accounts.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(data, f)


def run_start():
    import yaml
    with open('accounts.yaml') as f:
        data = yaml.safe_load(f)
        accounts = data['accounts']
        config = data['config']


    target_time = int(datetime.now().replace(hour=config['target_time'][0], minute=config['target_time'][1],second=config['target_time'][2]).timestamp())
    date = datetime(config['date'][0], config['date'][1], config['date'][2]).strftime('%Y-%m-%dT%H:%M:%S.000Z')

    processes = []
    for acc in accounts:
        cmd = [
            "python", "book.py",
            "--token", acc['token'],
            "--venueTypeId", config['venueTypeId'],
            "-c1", str(acc['court_1']),
            "-c2", str(acc['court_2']),
            "-t1", str(acc['time_1']),
            "-t2", str(acc['time_2']),
            "--target_time", str(target_time),
            "-d", str(date),
            "--User_Agent", config['User_Agent']
        ]
        p = subprocess.Popen(cmd)
        processes.append(p)

    # 等待所有进程完成
    for p in processes:
        p.wait()

if __name__ == '__main__':
    num = 2
    formatted_time = [22,0,0]
    target_time = int(datetime.now().replace(hour=formatted_time[0], minute=formatted_time[1],second=formatted_time[2]).timestamp())
    target_date=(datetime.now() + timedelta(days=3))

    # 生成yaml配置文件
    print("生成accounts.yaml...")
    generate_yaml(num,target_date,formatted_time)

    print("打开chrome浏览器...")
    drivers = []
    for i in range(num):
        port = 9220+i
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dir = os.path.join(current_dir, f"chrome_debug{i}")
        
        start_chrome_instance(port, dir) 

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://gym.sysu.edu.cn")
        drivers.append(driver)


    # 停止两分钟用于手动登录
    input('输入场地信息并完成登录后, 按Enter继续...')

    # 设置刷新间隔（单位：秒）
    refresh_interval = 5 * 60  # 每 5 分钟刷新一次
    
    try:
        while True:
            if time.time() < target_time - (7  * 60):      # 还未到预订时间的前7分钟内：反复刷新浏览器 
                print(f"{str(datetime.now())}\t刷新页面...")
                for i in range(num):
                    drivers[i].get("https://gym.sysu.edu.cn")
            else:
                break
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        print("手动终止循环")

    print(f'{str(datetime.now())}\t获取用户token ...')
    tokens = []
    for i in range(num):
        token = drivers[i].execute_script("return localStorage.getItem('scientia-session-authorization');")
        tokens.append(json.loads(token)["access_token"])

        drivers[i].quit()
        # 输出文件夹
    
    print("写入accounts.yaml...")
    update_token(tokens)

    print("运行订场脚本...")
    run_start()

    
    # 关闭页面，删除debug文件
    # 为了方便检查预订结果，还是手动删除吧

    # while time.time() < target_time + 20:
    #     time.sleep(10)
    # for i in range(num):
    #     current_dir = os.path.dirname(os.path.abspath(__file__))
    #     dir = os.path.join(current_dir, f"chrome_debug{i}")
    #     shutil.rmtree(dir)

