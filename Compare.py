	# -*- coding: utf-8 -*-
	import difflib
	import sys
	import time
	import datetime
	import threading
	import os
	from dingtalkchatbot.chatbot import DingtalkChatbot
	from qiniu import Auth, put_file, etag, urlsafe_base64_encode
	import qiniu.config
	import random

	webhook = 'XXXXXXXXXXXXXX'  #your DingRobotWebHook
	xiaoding = DingtalkChatbot(webhook)

	today = datetime.date.today()
	oneday = datetime.timedelta(days=1)
	
	yesterday = today - oneday
	res = ''
	timea = datetime.date.today()
	timea = str(timea)


	def Upload(dsthost):
	    #  Access Key  Secret Key
	    num = random.randint(0, 99)
	    access_key = 'XXXXX' 
	    secret_key = 'XXXXX'
	    # 构建鉴权对象
	    q = Auth(access_key, secret_key)
	    # 上传的空间name
	    bucket_name = 'XXXXX'
	    # 保存的文件名

	    key = dsthost + '_' + timea + 'report' + '.html'
	    print(key)
	    # key = '1.png'
	    # 生成上传 Token，可以指定过期时间等

	    token = q.upload_token(bucket_name, key, 3600)

	    # 要上传文件的本地路径
	    # localfile = '/usr/script/report/1.png'
	    localfile = '/usr/script/report/' + dsthost + '_' + timea + '_report.html'
	    ret, info = put_file(token, key, localfile)
	    print(info)
	    assert ret['key'] == key
	    assert ret['hash'] == etag(localfile)

	    yuming = 'XXXXX'  #your domain name
	    fileurl = yuming + '/' + key
	    return fileurl


	def readline(filename):
	    f = open(filename, encoding='gbk')
	    result = f.readlines()
	    return result


	def Compare(yes_lines, tod_lines, dsthost):
	    global res
	    dif = False
	    diffInstance = difflib.Differ()
	    diffList = list(diffInstance.compare(yes_lines, tod_lines))
	    for line in diffList:
	        if line[0] == '-':
	            dif = True
	    if dif == True:
	        res = res + '发现' + dsthost + '发生配置变动,生成比对结果报告......\n'
	        D = difflib.HtmlDiff()
	        fid = open('/usr/script/report/' + dsthost + '_' + timea + '_report.html', 'w')
	        global tod_conf_name
	        global yes_conf_name
	        fid.write(
	            D.make_file(yes_lines, tod_lines, fromdesc=yes_conf_name, todesc=tod_conf_name, context=True,
	                        numlines=0,
	                        charset='utf-8'))
	        time.sleep(0.5)
	        return True



	    else:
	        res = res + dsthost + '没有发生配置变动\n'


	def filter(lines):
	    list = []
	    for line in lines:
	        if "subscriber static name" not in line:
	            list.append(line)
	    return list


	if __name__ == '__main__':
	    res = res + '--------------------执行结果----------------------\n\n'
	    res = res + '执行自动化校对核心设备配置......\n\n'
	    for host in open(r'/usr/script/iplist/hxiplist.txt').readlines():
	        dsthost = host.strip('\n')
	        tod_conf_name = dsthost + '_' + str(today) + '.txt'
	        yes_conf_name = dsthost + '_' + str(yesterday) + '.txt'
	        yes_file = r'/usr/tftpboot/' + str(yesterday) + '/HX/' + yes_conf_name
	        tod_file = r'/usr/tftpboot/' + str(today) + '/HX/' + tod_conf_name
	        text1_lines = readline(yes_file)
	        text2_lines = readline(tod_file)
	        text3_lines = filter(text1_lines)
	        text4_lines = filter(text2_lines)
	        res = res + '执行' + dsthost + '校对函数......\n'
	        isDiff = Compare(text3_lines, text4_lines, dsthost)
	        if isDiff == True:
	            fileurl = Upload(dsthost)
	            xiaoding.send_link(title=dsthost + '_' + timea + '比对结果报告', text='点击查看', message_url=fileurl)
	xiaoding.send_text(msg=res)
