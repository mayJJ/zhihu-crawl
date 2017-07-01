# zhihu-crawl
requests + mongodb 爬取知乎所有用户信息 python3.5.2

看大神都爬知乎，我也爬了一下。
requests库请求 + xpath解析（绝世神器） + mongodb存储（易于横向扩展）

之前都用的mysql，看现在大家都力推mongodb，我也想着试一下，看看有什么特技。
在爬取的过程中，发现用户信息，并不是所有的用户都会填啊，基本都是选填。
对于这种，数据并不规范的情况， 确实mongodb更好，就算之前没有的字段，之后也可以插入添加

Login.py  
模拟登陆，

post表单，下载验证码。填写账号、密码之后。向服务器发送post请求。
这里的验证码是直接请求的简单的验证码的链接。毕竟倒着的字，不会破解。

Spider.py
主程序
主程序原理其实大家应该都很清楚啦。简单的爬虫原理，一个url如何，下载页面信息，解析得到数据和url。url放入待爬取的队列，需要的数据就用于持久化。
大家仔细观察，可以发现，在关注列表里，把鼠标放在用户头像上，会出来一个ajax请求。json的格式，简直是最好提取的了。那就json模块解析咯。

我在知乎专栏写过一篇非常非常详细的文章。专门讲ajax动态加载以及数据爬取方法的。

附上链接：
https://zhuanlan.zhihu.com/p/27346009

然后当我们拿到一页的数据后，就想着要翻页了，那之后的数据。仔细观察发现多了一个动态参数，page=?  都说了page了，那我们就只需要自己去构造这个page
的大小。

然后问题又来了，我怎么知道有多少页呢。其实爬虫多了应该就有经验了。
    1、如果可以直接拿到页码的，那就直接拿。
    2.但是，一般来说，页码的格式都是1.2.3........下一页。那怎么办？其实这也靠经验发现。在我们拿到的列表的页面中，可能会存在page或者total的参数，
    一般来说，就是页码或者总数了。有了一个都行，总数我们可以用除法得到嘛。
    3.如果你真的都实在找不到。那就通用的大招了，不要管，我就继续爬。但是我做一个异常处理，如果我需要的数据在这个页面没有，那我就退出这个请求方法。
    
    
    然后爬虫界的又最常见问题。去重。
    这方法真的还是很多。以我的经验，当然很狭隘。大概三种方法。
    
    1.  数据结构。数据结构是什么，数据结构是用来存储的，python中有个东西 ，叫做集合。它的特点在于，无序且不重复。如果我们对于爬取的数据没有顺序的
    要求。尽管用它吧，它会帮你筛选的。
    2.  数据库下手。我们的数据都是要放入数据库的，只要我们放进去之前，先看看它有没有在数据库里面不就好了吗。如果在，我就pass，不在，就插入。
    但是，想想，当数据特别特别多的时候，每插入一次，我们先得查找数据库。那得有多大的资源耗损啊。
    3. redis。redis是一个内存型的数据库。所以查找起来很快，所以我们可以先放内存中。不过本人小白一个，还没用过这种方法，用了再写一篇详细讲解。
    
    
    
  DataPersistence.py
  数据持久化
  
  刚接触monggodb的时候，有一点怪怪的感觉。为啥呢？本人处女座，特别担心数据不完整，心里就担心。mongodb没有事务的概念，没有事务就不能回滚。那如果数据
  插入的过程发生异常，数据咋办呢？后来同学说我，多虑了。在爬虫的数据量面前，损失一些数据并不会影响整体结果。不过，有知道的同学请告诉我，其中的原理。
  
  最近接触了flask，大爱。正在学习flask-api的用法， 想在DataPersistence.py 中提供多种数据库的方法。有时间了再写文章讲讲。最近找暑假实习，比较忙，
  先到此为止。
  
  Config 和 Proxies还没有写。
  想自己维护一个完整的代理项目。所以先留着。Config在大型项目中，也是很重要的。因为此次练练手，等有时间再写吧。这就是一个非常简单的爬虫，基本的日志打印，
  celery + redis 实现分布式，都还没使用。一起努力吧。
