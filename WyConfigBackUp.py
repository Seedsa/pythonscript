#
import paramiko
import time
import threading
import datetime
import os
from dingtalkchatbot.chatbot import DingtalkChatbot

webhook = 'your DingRobot WebHook'
ding = DingtalkChatbot(webhook)
resault = ''

tftpserver = "your tftpserver ip address"


class Bakconf(threading.Thread):
    def __init__(self, host, username, password):
        threading.Thread.__init__(self)
        self.host = host
        self.username = username
        self.password = password

    def run(self):
        try:
        	# 建立客户端
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host, 22, self.username, self.password, timeout=5)
            print("Ssh is Connected Now!")
            remote = ssh.invoke_shell()
            # 格式化配置文件保存例：
            nowTime = datetime.datetime.now().strftime('%Y-%m-%d')
            filename = str(self.host) + '_' + nowTime + '.txt'
            remote.send('enable\n')
            remote.send('XXXXXXXX\n')#your enable password
            remote.send('copy flash:/config.text tftp://' + tftpserver + '/' + nowTime + '/WY' + '/' + filename + '\n')
            time.sleep(1)
            remote.send('exit\n')
            print('done')
            ssh.close()
        except:
            ding.send_text(msg=self.hot + '备份失败,请联系管理员')


def main():
    ding.send_text(msg='开始多线程备份物业设备配置...')
    time.sleep(1)
    username = "XXXXXXXX"# your ssh username
    password = "XXXXXXXXX" # your ssh password
    nowTime = datetime.datetime.now().strftime('%Y-%m-%d')
    if os.path.exists('/usr/tftpboot/' + nowTime) == False:
        os.mkdir('/usr/tftpboot/' + nowTime)
        os.system('chmod 777 ' + '/usr/tftpboot/' + nowTime)
    if os.path.exists('/usr/tftpboot/' + nowTime + '/WY') == False:

        os.mkdir('/usr/tftpboot/' + nowTime + '/WY')
        os.system('chmod 777 ' + '/usr/tftpboot/' + nowTime + '/WY')
    for host in open(r'/usr/script/iplist/wyiplist.txt').readlines():
        dsthost = host.strip('\n')
        backconf = Bakconf(dsthost, username, password)
        backconf.start()
    if resault == '':
        ding.send_text(msg=nowTime + ' 物业网设备配置备份完成')
    elif resault != '':
        ding.send_text(msg=nowTime + ' 物业网设备配置备份完成' + resault)


if __name__ == '__main__':
    main()
