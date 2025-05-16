import ctypes
import json
import smtplib
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from curl_cffi import requests
import time
import os

# 定义存储已处理房源信息的文件路径
PROCESSED_HOUSES_FILE = "processed_houses.json"

# 加载已处理的房源信息
def load_processed_houses():
    if os.path.exists(PROCESSED_HOUSES_FILE):
        with open(PROCESSED_HOUSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 保存已处理的房源信息
def save_processed_houses(houses):
    with open(PROCESSED_HOUSES_FILE, "w", encoding="utf-8") as f:
        json.dump(houses, f, ensure_ascii=False, indent=2)

def send_email(tousers,mail_content):
	mail_title = 'find new house'
	senderName = "myself"
	# tourser = '39664269@qq.com'
	
	host_server = 'smtp.qq.com'
	sender = '1796170111@qq.com'
	code='ibfyjxpcjlovbcfb'

	for touser in tousers:
		msg = MIMEText(mail_content, _subtype='plain', _charset='utf-8')
		msg['Accept-Language'] = 'zh-CN'
		msg['Accept-Charset'] = 'ISO-8859-1,utf-8'
		msgAtt = MIMEMultipart()
		msgAtt.attach(msg)
		msg['Subject'] = mail_title 
		msg['From'] = formataddr(pair=(senderName, sender)) 
		smtp = smtplib.SMTP_SSL(host_server,465)
		smtp.login(sender, code)
		msg['To'] = touser
		smtp.sendmail(sender, touser, msg.as_string())
		print(mail_title,f"send mail to {touser} sucess！")
	
	# for touser in tousers:
	# 	print(f'send mail to {touser}')
	# 	msg['To'] = touser
	# 	smtp.sendmail(sender, touser, msg.as_string())
	# 	print(mail_title,f"send mail to {touser} sucess！")
	smtp.quit()
	return

def get_items(price_max):
	proxies={ 'http':'127.0.0.1:10809','https':'127.0.0.1:10809'}
	headers = {
	"accept": "*/*",
	"accept-language": "zh-CN,zh;q=0.9",
	"content-type": "application/json",
	"origin": "https://holland2stay.com",
	"priority": "u=1, i",
	"sec-ch-ua": "\"Not;A=Brand\";v=\"24\", \"Chromium\";v=\"128\"",
	"sec-ch-ua-mobile": "?0",
	"sec-ch-ua-platform": "\"Windows\"",
	"sec-fetch-dest": "empty",
	"sec-fetch-mode": "cors",
	"sec-fetch-site": "same-site",
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
	}
	url = "https://api.holland2stay.com/graphql/"
	data = {
	"operationName": "GetCategories",
	"variables": {
		"currentPage": 1,
		"filters": {
		"city": {
			"eq": "25"
		},
		"available_to_book": {
			"eq": "179"
		},
		"finishing": {
			"in": [
			"70",
			"6261"
			]
		},
		"category_uid": {
			"eq": "Nw=="
		}
		},
		"pageSize": 10,
		"sort": {
		"available_startdate": "ASC"
		}
	},
	"query": "query GetCategories($pageSize: Int!, $currentPage: Int!, $filters: ProductAttributeFilterInput!, $sort: ProductAttributeSortInput) {\n  products(\n	pageSize: $pageSize\n	currentPage: $currentPage\n	filter: $filters\n	sort: $sort\n  ) {\n	...ProductsFragment\n	__typename\n  }\n}\n\nfragment ProductsFragment on Products {\n  sort_fields {\n	options {\n	  label\n	  value\n	  __typename\n	}\n	__typename\n  }\n  aggregations {\n	label\n	count\n	attribute_code\n	options {\n	  label\n	  count\n	  value\n	  __typename\n	}\n	position\n	__typename\n  }\n  items {\n	name\n	sku\n	city\n	url_key\n	available_to_book\n	available_startdate\n	next_contract_startdate\n	current_lottery_subscribers\n	building_name\n	finishing\n	living_area\n	no_of_rooms\n	resident_type\n	offer_text_two\n	offer_text\n	maximum_number_of_persons\n	type_of_contract\n	price_analysis_text\n	allowance_price\n	floor\n	basic_rent\n	lumpsum_service_charge\n	inventory\n	caretaker_costs\n	cleaning_common_areas\n	energy_common_areas\n	energy_label\n	minimum_stay\n	allowance_price\n	small_image {\n	  url\n	  label\n	  position\n	  disabled\n	  __typename\n	}\n	thumbnail {\n	  url\n	  label\n	  position\n	  disabled\n	  __typename\n	}\n	image {\n	  url\n	  label\n	  position\n	  disabled\n	  __typename\n	}\n	media_gallery {\n	  url\n	  label\n	  position\n	  disabled\n	  __typename\n	}\n	price_range {\n	  minimum_price {\n		regular_price {\n		  value\n		  currency\n		  __typename\n		}\n		final_price {\n		  value\n		  currency\n		  __typename\n		}\n		discount {\n		  amount_off\n		  percent_off\n		  __typename\n		}\n		__typename\n	  }\n	  maximum_price {\n		regular_price {\n		  value\n		  currency\n		  __typename\n		}\n		final_price {\n		  value\n		  currency\n		  __typename\n		}\n		discount {\n		  amount_off\n		  percent_off\n		  __typename\n		}\n		__typename\n	  }\n	  __typename\n	}\n	__typename\n  }\n  page_info {\n	total_pages\n	__typename\n  }\n  total_count\n  __typename\n}"
	}
	try:
		response = requests.post(url, headers=headers, json=data, impersonate='chrome119')
		print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " 本次请求响应码：", response.status_code)

		##------处理获得的数据--------------
		# 加载已经保存的数据
		processed_houses = load_processed_houses()
		jsp = response.json()
		house_items = []
		mail_content = ""
		for item in jsp['data']['products']['items']:
			if item['basic_rent'] < price_max:
				new_house = {
					"name": item['name'],
					'basic_rent': item['basic_rent'],
					'living_area': item['living_area'],
					'url': f'https://holland2stay.com/residences/{item["url_key"]}.html'
					}

				# 检查是否为新房源
				if new_house not in processed_houses:
					house_items.append(new_house)
					processed_houses.append(new_house)
					save_processed_houses(processed_houses)  # 保存已处理的房源信息到文件中
					mail_content += f"name:{new_house['name']},basic_rent:{new_house['basic_rent']},living_area:{new_house['living_area']},url:{new_house['url']}\n"
					print("find new house:", new_house)

		if house_items:
			send_email(['3552144578@qq.com','2875049136@qq.com'],mail_content)
	except requests.exceptions.Timeout:
		print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " 请求超时，请检查网络连接。")
	except Exception as e:
		print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " 程序出错，请检查:", e)
		send_email(['3552144578@qq.com'],f"程序出错，请检查:{e}")

def main():
	price_max = 99999

	ES_CONTINUOUS = 0x80000000
	ES_SYSTEM_REQUIRED = 0x00000001
	ES_DISPLAY_REQUIRED = 0x00000002


	while True:
		try:
			get_items(price_max)
		except Exception as e:
			print(f"程序出错，请检查:{e}")
			send_email(['3552144578@qq.com'],f"程序出错，请检查:{e}")
		ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
		time.sleep(20)


if __name__ == "__main__":
	
	main()