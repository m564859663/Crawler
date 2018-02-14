# 网络爬虫练习笔记、实例
## 2018-2-14
    更新了今日头条、妹子图的实例
toutiao.py中含有json.load, BeautifulSoap, re正则表达式的用法, md5码存储, 以及开启多线程、建立MongoDB数据库的方法
meizitu.py为根据头条爬虫进行的实例练习，与toutiao.py中的方法基本一致
```python
# soup.select的方法
article_url = soup.select('#maincontent')  # id
article_url = soup.select('.metaRight')  # class
article_url = soup.select('h2')  #
```
