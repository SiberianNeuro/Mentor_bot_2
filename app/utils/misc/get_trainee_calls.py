import aiohttp
from datetime import date


async def get_calls(phone_number: str) -> str:
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
            "date_from": f"{str(date.today())} 00:00:00",
            "date_till": f"{str(date.today())} 23:59:59",
            "fields": [
                "id",
                "is_lost",
                "direction",
                "start_time",
                "call_records",
                "contact_phone_number",
                "virtual_phone_number",
                "employees"
            ]
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://dataapi.uiscom.ru/v2.0", json=params) as response:
            data = await response.json()
    string = ''
    try:
        for num, call in enumerate(data['result']['data']):
            string += f'<b>{num}</b>: https://app.uiscom.ru/system/media/talk/{call["communication_id"]}/{call["call_records"][0]}/\n'
    except KeyError:
        string = 'Звонков не найдено.'
    return string
