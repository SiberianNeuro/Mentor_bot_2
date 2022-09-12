import aiohttp
from datetime import date


async def get_calls(phone_number: str, call_date: str) -> str:
    print(call_date)
    print(phone_number)
    params = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "get.calls_report",
        "params": {
            "filter": {
                "filters": [
                    {
                        "field": "virtual_phone_number",
                        "operator": "=",
                        "value": phone_number
                    },
                    {
                        "field": "is_lost",
                        "operator": "=",
                        "value": False
                    }
                ],
                "condition": "and"
            },
            "offset": 0,
            "limit": 10000,
            "access_token": "e5kzqpauylsjtb2r5vkam8d0ubb0ubejejc6qc0o",
            "date_from": f"{call_date} 00:00:00",
            "date_till": f"{call_date} 23:59:59",
            "fields": [
                "id",
                "is_lost",
                "direction",
                "start_time",
                "call_records",
                "communication_id",
                "clean_talk_duration",
                "contact_phone_number",
                "virtual_phone_number",
                "employees"
            ]
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://dataapi.uiscom.ru/v2.0", json=params) as response:
            res = await response.json()
    string = ''
    if res['result']:
        if res['result']['data']:
            for num, call in enumerate(res['result']['data'], 1):
                dir = "Входящий" if call['direction'] == 'in' else "Исходящий"
                string += f'<b>{num}</b>: <i>{call["start_time"].split()[1]}</i> | {call["contact_phone_number"]} | {dir} | {call["clean_talk_duration"]} сек.\n' \
                          f'https://app.uiscom.ru/system/media/talk/{call["communication_id"]}/{call["call_records"][0]}/\n'
        else:
            string = 'Звонков не найдено.'
    else:
        string = 'Звонков не найдено.'
    return string
