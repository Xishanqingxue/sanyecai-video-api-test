# -*- coding:utf-8 -*-
import smtplib, os, settings, datetime,random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from base.base_log import BaseLogger

logger = BaseLogger(__name__).get_logger()


class BaseMail(object):

    def __init__(self):
        self.report_dir_path = settings.REPORT_DIR_PATH
        self.image_dir_path = './image/'
        self.report_file = self._get_new_report()

    def _get_new_report(self):
        """
        获取最新测试报告
        :return:
        """
        lists = os.listdir(self.report_dir_path)
        lists.sort(key=lambda fn: os.path.getmtime(self.report_dir_path + '/' + fn))
        file_new = os.path.join(self.report_dir_path, lists[-1])
        logger.info('The latest test report is a success.')
        logger.info('Report path:{0}'.format(os.path.abspath(file_new)))
        return file_new

    def send_mail(self):
        """
        发送测试报告附件邮件
        :return:
        """
        msg = MIMEMultipart()
        msg['Subject'] = settings.MAIL_HEADER
        msg['From'] = settings.MAIL_FROM
        msg['To'] = 'all'
        msg['Accept-Language'] = 'zh-CN'
        msg["Accept-Charset"] = "ISO-8859-1,utf-8"

        # 测试报告H5源码为邮件主体
        html_msg = open(self.report_file,'r',encoding="utf-8").read()
        msg.attach(MIMEText(html_msg, 'html', 'utf-8'))

        # 邮件主体与附件之间通过一张随机图片隔开
        image_dir_list = os.listdir(self.image_dir_path)
        num = random.randint(0,len(image_dir_list) - 1)
        image = os.path.join(self.image_dir_path,image_dir_list[num])
        image_file = open(image,'rb')
        msg_image = MIMEImage(image_file.read())
        image_file.close()
        msg_image.add_header('Content-ID', '<image1>')
        msg.attach(msg_image)

        # 测试报告附件的描述
        pure_text = MIMEText('详细测试报告请见附件！',_charset='utf-8')
        pure_text['Accept-Language'] = 'zh-CN'
        pure_text["Accept-Charset"] = "ISO-8859-1,utf-8"
        msg.attach(pure_text)

        # HTML格式的附件
        html_application = MIMEApplication(open(self.report_file, 'rb').read())
        file_name = 'Ajax接口自动化测试报告详细版-{0}.html'.format((datetime.datetime.now()).strftime("%Y%m%d"))
        html_application.add_header('Content-Disposition', 'attachment', filename=file_name)
        msg.attach(html_application)

        try:
            # 链接163邮箱服务器
            client = smtplib.SMTP()
            client.connect(settings.MAIL_SERVER)
            logger.info('SMTP Server connection succeeded.')
            # 登录163邮箱
            client.login(settings.MAIL_FROM, settings.MAIL_FROM_PASSWORD)
            logger.info('SMTP Server login succeeded.')
            # 发送邮件
            client.sendmail(settings.MAIL_FROM, settings.MAIL_TO, msg.as_string())
            logger.info('Email sent to {0} successfully!'.format(settings.MAIL_TO))
            # 关闭链接
            client.quit()
        except Exception:
            logger.error('Email sent failed!')
            pass