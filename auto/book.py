import requests
import time
from datetime import datetime, timedelta
import uuid
import argparse
import re

VenueIds={0:None,
          1:"8155aa2b-4cb0-4402-9d8a-4b5afcf4a19b",
          2:"19cb723c-67ad-4729-b27e-586ca1639fa8",
          3:"c13e4524-d62f-485e-b61b-a1c467baada9",
          4:"9e3bfc17-954d-43c5-9e36-9afd3a35c6ff",
          5:"7588d74f-24d4-4903-8373-e19daf0e1dab",
          6:"7a84af6e-e82d-4279-b949-f92c8f3e9343",
          7:"b22b1a38-1d7b-4f8d-9be8-36e3c8733db6",
          8:"bcd075c4-081d-427b-b6d7-5f3d7a6cade9",
          9:"b9605fe6-b0f5-49d9-a3de-5fdf02988cf9",
          10:"56dc01eb-69f5-4da4-8b3d-9ef433f08e28",
          12:"0f895fec-efc2-4cc2-b6d7-9032c98ff2f8",
          13:"cf865975-332d-48b7-93f8-a5a8fda4e113",
          14:"4011dac1-f929-444e-a6f7-b456eb069f91"}

venueNames={0:"东校园体育馆羽毛球场-场地0",
            1:"东校园体育馆羽毛球场-场地1",
          2:"东校园体育馆羽毛球场-场地2",
          3:"东校园体育馆羽毛球场-场地3",
          4:"东校园体育馆羽毛球场-场地4",
          5:"东校园体育馆羽毛球场-场地5",
          6:"东校园体育馆羽毛球场-场地6",
          7:"东校园体育馆羽毛球场-场地7",
          8:"东校园体育馆羽毛球场-场地8",
          9:"东校园体育馆羽毛球场-场地9",
          10:"东校园体育馆羽毛球场-场地10",
          12:"东校园体育馆羽毛球场-场地12",
          13:"东校园体育馆羽毛球场-场地13",
          14:"东校园体育馆羽毛球场-场地14"}

def set_args():
    parser = argparse.ArgumentParser(
        description="单账户订场脚本",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('--token', type=str, default=None, help='用户token信息')
    parser.add_argument('--venueTypeId',type=str, default='99f5f83b-2adc-41b6-8c98-901ced354551', help='校区球场id, 当前只支持东校区球场')
    parser.add_argument('-c1','--court_1', type=int, default=10, help='球场一编码, 默认10号场')
    parser.add_argument('-c2','--court_2', type=int, default=None, help='球场二编码, 默认为空')
    parser.add_argument('-t1','--time_1', type=int, default=20, help='球场一开始时间, 默认20点')
    parser.add_argument('-t2','--time_2', type=int, default=21, help='球场一开始时间, 默认21点')
    parser.add_argument('--target_time', type=int, default=int(datetime.now().replace(hour=22, minute=0,second=0).timestamp()), help='到点预订时间, 默认当天22点')
    parser.add_argument('-d', '--date', type=str, default=datetime(2025, 4, 10).strftime('%Y-%m-%dT%H:%M:%S.000Z'), help="预约日期, 默认2025-04-10")
    parser.add_argument('--User_Agent', type=str, default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', help='浏览器版本')

    return parser.parse_args()              

class GymBooker:
    def __init__(self, token, venueTypeId, target_time, User_Agent):
        self.session = requests.Session()
        self.token = token
        self.venueTypeId = venueTypeId
        self.headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': User_Agent,
        }
        self.target_time = target_time
        self.user_id = self._get_user_identity()
    

    def _get_user_identity(self):
        """获取用户唯一标识"""
        # 从用户信息接口获取真实Identity
        profile_url = "https://gym.sysu.edu.cn/api/Credit/Me"
        resp = self.session.get(
                    profile_url,
                    headers=self.headers,
                )

        if resp.status_code == 200:
            return resp.json()['Identity']
        else:
            print('身份信息过期')
            return 'f'
        

    def get_available_slots(self, days=3):
        """动态获取可预约时段"""
        date_format = "%Y-%m-%d"
        start_date = datetime.now().strftime(date_format)
        end_date = (datetime.now() + timedelta(days=days)).strftime(date_format)
        params = {
            "venueTypeId": self.venueTypeId,
            "start": start_date,
            "end": end_date
        }
        
        resp = self.session.get(
            "https://gym.sysu.edu.cn/api/venue/available-slots/range",
            params=params,
            headers=self.headers,
        )

        return resp.json()

    def generate_booking_payload(self, venue_info):
        """构建订场请求数据包"""
        # 生成合规UUID
        booking_id = str(uuid.uuid4())
        identity = str(uuid.uuid4())
        # 获取用户信息
        if self.user_id == 'f':
            return {}
        
        # 时间格式转换
        booking_date = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
        slot_date = venue_info['date']
        if venue_info['venueId2'] == None:
            return {
                "Identity": identity,
                "BookingId": booking_id,
                "VenueTypeId": self.venueTypeId,
                "ActionedBy": self.user_id,
                "Charge": venue_info['charge'],
                "CreatedAt": booking_date,
                "UpdatedAt": booking_date,
                "Description": "东校园体育馆羽毛球场",
                "IsCash": False,
                "Participants": [],
                "Status": "Accepted",
                "VenueBookings": [
                    {
                        "VenueId": venue_info['venueId1'],
                        "VenueName": venue_info['venueName1'],
                        "TimeSlots": [{
                            "Date": slot_date,
                            "Start": venue_info['start1'],
                            "End": venue_info['end1']
                        }]
                    }
                ]
            }
        else: 
            return {
                "Identity": identity,
                "BookingId": booking_id,
                "VenueTypeId": self.venueTypeId,
                "ActionedBy": self.user_id,
                "Charge": venue_info['charge'],
                "CreatedAt": booking_date,
                "UpdatedAt": booking_date,
                "Description": "东校园体育馆羽毛球场",      # 好像不带该属性会出错
                "IsCash":  True,#False,                        # 好像不带该属性会出错
                "Participants": [],
                "Status": "Accepted",
                "VenueBookings": [
                    {
                        "VenueId": venue_info['venueId1'],
                        "VenueName": venue_info['venueName1'],
                        "TimeSlots": [{
                            "Date": slot_date,
                            "Start": venue_info['start1'],
                            "End": venue_info['end1']
                        }]
                    },{
                        "VenueId": venue_info['venueId2'],
                        "VenueName": venue_info['venueName2'],
                        "TimeSlots": [{
                            "Date": slot_date,
                            "Start": venue_info['start2'],
                            "End": venue_info['end2']
                        }]
                    }
                ]
            }

    def book_court(self, venue_data):
        """执行预约核心逻辑"""
        api_url = "https://gym.sysu.edu.cn/api/BookingRequestVenue"
        payload = self.generate_booking_payload(venue_data)
        if payload == {}:
            return []
        count  = 0
        while True:
            if count > 10:
                return False
            if time.time() >= self.target_time - 0.05:
                resp = self.session.post(
                    api_url,
                    json=payload,
                    headers=self.headers,
                )
                # if resp.status_code != 200:
                #     print(f'[{self.user_id}]\t该账号不可预约')
                #     return []
                if resp.json()['Code'] == 200:
                    VenueBookings = resp.json()['Result']['VenueBookings']
                    for VenueBooking in VenueBookings:
                        VenueName = VenueBooking['VenueName']
                        TimeSlots = VenueBooking['TimeSlots']
                        start = TimeSlots[0]['Start']
                        End = TimeSlots[0]['End']
                        print(f'[{self.user_id}]\t{VenueName}\t{start}-{End}')
                    return []
                elif resp.json()['Code'] == 400:
                    res = resp.json()['Result']
                    print(f'[{self.user_id}]\t{res}')
                    if res == '该日期不可预约' or res == '系统繁忙，请重试。':
                        time.sleep(0.08)
                        count = count + 1
                    elif res == '该时段不可预约，请选择别的时段。':
                        courts = self.get_available_slots(3)
                        available_courts1 = self.find_available_courts(courts,venue_data['start1'],venue_data['date'])
                        available_courts2 = self.find_available_courts(courts,venue_data['start2'],venue_data['date'])
                        return [available_courts1, available_courts2]
                    else:   # 'You have reached the limit.'
                        return []    

    def find_available_courts(self, venues_data: list, target_time: str, target_date: str = None) -> list:
        """
        查找指定日期和时间段可用的场地编号
        
        :param venues_data: 场地数据列表
        :param target_time: 目标时间段(格式: HH:mm 或 HH: mm)
        :param target_date: 目标日期(默认当天，格式: YYYY-MM-DD)
        :return: 按数字排序的可用场地编号列表
        """
        # 标准化输入参数
        current_date = target_date.split('T')[0]

        # 场地匹配模式（兼容多种命名格式）
        pattern = re.compile(r'场地\s*(\d+)')
        
        available = set()
        
        for venue in venues_data:
            # 提取场地编号
            match = pattern.search(venue['VenueName'])
            if not match:
                continue
            court_num = int(match.group(1))
            
            # 筛选有效时段
            valid_slots = [
                slot for slot in venue['Timeslots']
                if slot['Date'] == current_date
                and slot['Start'] == target_time
                and slot['AvailableCapacity'] > 0
            ]
            
            if valid_slots:
                available.add(court_num)
        
        return sorted(available)

if __name__ == '__main__':

    args = set_args()

    venue_data = {
        "venueId1": VenueIds[args.court_1],
        "venueName1": venueNames[args.court_1],
        "start1": f"{args.time_1:02d}:00",
        "end1": f"{(args.time_1+1):02d}:00",
        "venueId2": VenueIds[args.court_2],
        "venueName2": venueNames[args.court_2],
        "start2": f"{args.time_2:02d}:00",
        "end2": f"{(args.time_2+1):02d}:00",
        "charge": 30,
        "date": args.date
    }

    booker = GymBooker(args.token, args.venueTypeId, args.target_time, args.User_Agent)

    result = booker.book_court(venue_data)
    # 预约该时间段其他场地
    if result != []:
        for r1 in result[0]:
            venue_data = {
                "venueId1": VenueIds[r1],
                "venueName1": venueNames[r1],
                "start1": f"{args.time_1:02d}:00",
                "end1": f"{(args.time_1+1):02d}:00",
                "venueId2": None,
                "start2": f"{args.time_1:02d}:00",
                "charge": 30,
                "date": args.date
            }
            if booker.book_court(venue_data) == []:
                break
        for r2 in reversed(result[1]):
            venue_data = {
                "venueId1": VenueIds[r2],
                "venueName1": venueNames[r2],
                "start1": f"{args.time_2:02d}:00",
                "end1": f"{(args.time_2+1):02d}:00",
                "venueId2": None,
                "start2": f"{args.time_2:02d}:00",
                "charge": 30,
                "date": args.date
            }
            if booker.book_court(venue_data) == []:
                break