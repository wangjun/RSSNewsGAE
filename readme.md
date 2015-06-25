# StockNewsGAE
 

- 成品范例见：https://s.liantian.me/


- 抓取feed上的财经新闻，使第三方库feedparser分析。

- 对每条纪录，使用jieba分词进行关键词提取。

- 允许用户设置自己关心的关键词，并只显示包含关键词的新闻条目。

- 每抓取一个新闻，如果满足某个用户的关键词，则用PushOver推送到这个用户的手机端。


分词需要配合 https://github.com/geeklian/Jieba-GAE 使用