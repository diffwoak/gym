import subprocess
import yaml
from datetime import datetime

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
