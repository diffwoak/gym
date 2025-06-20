from collections import defaultdict
from datetime import datetime
from book import GymBooker

def parse_venue_data(data, date):
    """解析并重组数据结构"""
    timeline = defaultdict(lambda: defaultdict(str))
    venues = set()
    
    for venue in data:
        # 提取场地编号（如：场地1）
        venue_num = venue['VenueName'].split('-')[-1].strip()
        venues.add(venue_num)
        
        for slot in venue['Timeslots']:
            if datetime.fromisoformat(slot['Date']).date() != date:
                continue
                
            time_key = f"{slot['Start']}-{slot['End']}"
            status = "xxx"  # 默认不可预订
            if slot['AvailableCapacity'] > 0:
                status = f"√"
            elif slot['AvailableCapacity'] == 0:
                status = " "
                
            timeline[time_key][venue_num] = status
    
    # 按时间排序（08:00-09:00, 09:00-10:00,...）
    sorted_times = sorted(timeline.keys(), key=lambda x: x.split('-')[0])
    # 按场地编号排序（场地1, 场地2,... 场地10）
    sorted_venues = sorted(venues, key=lambda x: int(x[2:]))
    
    return sorted_times, sorted_venues, timeline

def print_rotated_table(times, venues, timeline):
    """打印矩阵转置后的表格"""
    # 表头：场地编号
    header = ["时段"] + [f" {v} " for v in venues]
    
    # 计算列宽
    col_width = [max(len(t) for t in times)] + [max(len(v), 8) for v in venues]
    
    # 打印表格边界
    top_border = "┌" + "┬".join("─"*(w) for w in col_width) + "┐"
    print(top_border)
    
    # 打印表头
    header_row = "│" + "│".join(
        f"{h:^{col_width[i]-2}}" for i, h in enumerate(header)
    ) + "│"
    print(header_row)
    
    # 打印分隔线
    sep_line = "├" + "┼".join("─"*w for w in col_width) + "┤"
    print(sep_line)
    
    # 打印数据行
    for time_slot in times:
        cells = [time_slot] + [timeline[time_slot].get(v, "xxx").center(col_width[i+1]) 
                              for i, v in enumerate(venues)]
        row = "│" + "│".join(
            f"{cell:^{col_width[i]}}" for i, cell in enumerate(cells)
        ) + "│"
        print(row)
    
    # 打印底部边界
    bottom_border = "└" + "┴".join("─"*w for w in col_width) + "┘"
    print(bottom_border)


if __name__ == '__main__':
    # 配置用户信息、查询日期
    token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjI1QjExQTk3MDQ0Qjc5MUVGN0I2MDAzOTdDMzk2MDJDQzA1RjY5NTYiLCJ4NXQiOiJKYkVhbHdSTGVSNzN0Z0E1ZkRsZ0xNQmZhVlkiLCJ0eXAiOiJKV1QifQ.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoiY2hlbnh5ODM1IiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbmFtZWlkZW50aWZpZXIiOiJjaGVueHk4MzUiLCJodHRwOi8vc2NpZW50aWEuY29tL2NsYWltcy9JbnN0aXR1dGlvbiI6IjRmYjM3ZTI4LTBhOTAtNGJiMC1iMGUwLWI3OThlY2U2ZjMyMCIsImh0dHA6Ly9zY2llbnRpYS5jb20vY2xhaW1zL0luc3RpdHV0aW9uTmFtZSI6Im1haWwuc3lzdSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL2VtYWlsYWRkcmVzcyI6ImNoZW54eTgzNUBtYWlsLnN5c3UuZWR1LmNuIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvZ2l2ZW5uYW1lIjoiY2hlbnh5ODM1IiwiaHR0cDovL3NjaWVudGlhLmNvbS9jbGFpbXMvU2NvcGUiOiJSQiIsIm5iZiI6MTc1MDE1NTc1MCwiZXhwIjoxNzUwMTU5MzUwLCJpc3MiOiJodHRwczovL2xvY2FsaG9zdC8iLCJhdWQiOiJodHRwOi8vcmVzb3VyY2Vib29rZXJhcGkuY2xvdWRhcHAubmV0LyJ9.BA5voOZIbsy4c3wcwfYJdYTBJzwWRQOQee6KmArg5YJvIqC3MO92Tnd4ZuypkOfLe8Wj9urYVmP_VKB1mDCEuPzy8n_RcK8_e4Y_PxwzJ1Fd1Kl_6jUWXF0rdtlnzvOcZGMcSXUaFSirIDuPQNF2dcfROEE_Xhmc-LFD_2B2I26LwbelY8wiYvMs5ns0dRVkmJu44Qw41Fh9bXCgwmBKJK65VwGTfWhOHKsC-ca3JBp77I03mklyrhON0-drmS80BKRX_8fqnv59jIuShHXXLnOXDZ7L7Uo1nn_cBUkAnJzP5ifZuarFS4jQOL-dmWhk8tT_djJYMK4i9g8IMaxxJA'
    bot = 'AKwaNwoAAAAAAAAAAAAAAABnTGl9lwEAANxsV97Map20UTHeCfQysNzpAzge'
    date = datetime(2025, 6, 20).date()


    venueTypeId= '99f5f83b-2adc-41b6-8c98-901ced354551' # 东校
    # venueTypeId= 'c4f06a7d-bb6b-4a2f-9626-7bebfc4f09ae' # 南校
    target_time = int(datetime.now().replace(hour=0, minute=0,second=0).timestamp())
    User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'

    booker = GymBooker(token, bot, venueTypeId, target_time, User_Agent)

    raw_data = booker.get_available_slots(10)
    times, venues, timeline = parse_venue_data(raw_data, date)
    print(f"Date: {date}")
    print_rotated_table(times, venues, timeline)


