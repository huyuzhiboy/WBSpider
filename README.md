This is a weibo spider with web interface.

部署流程：
1、修改yum源并更新系统
2、安装pip，https://pip.pypa.io/en/stable/installing/，下载并执行python get-pip.py
3、pip install requests
4、pip install django
5、yum install git python-devel libffi libffi-devel libxslt-devel libxml2-devel openssl-devel
6、pip install scrapy
7、git clone https://github.com/simon582/WBSpider.git
8、cd进入WBSpider目录，新建两个目录为temp和log
9、sh start.sh 启动脚本
10、通过浏览器访问：http://主机IP:8080/?wbid=xxx&max_wb_page=1&max_cmt_page=1，max_wb_page表示最大抓取的微博页数，max_cmt_page表示最大抓取的评论页数。
