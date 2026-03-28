import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime

# 新闻网站配置 - 优化选择器和内容提取
NEWS_SOURCES = [
    {
        'name': '新浪财经',
        'url': 'https://finance.sina.com.cn',
        'search_url': 'https://search.sina.com.cn/?q={keyword}&range=all&c=news',
        'selector': '.news-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': None
    },
    {
        'name': '新浪财经滚动',
        'url': 'https://finance.sina.com.cn/roll/',
        'selector': 'li',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': None
    },
    {
        'name': '新浪财经新闻',
        'url': 'https://finance.sina.com.cn/news/',
        'selector': 'li',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': None
    },
    {
        'name': '上海证券报',
        'url': 'https://www.cnstock.com',
        'search_url': 'https://www.cnstock.com/search?keyword={keyword}',
        'selector': '.newslist li',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': 'span'
    },
    {
        'name': '第一财经',
        'url': 'https://www.yicai.com',
        'search_url': 'https://www.yicai.com/search?keyword={keyword}',
        'selector': '.news-list-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.news-list-time'
    },
    {
        'name': '证券时报',
        'url': 'https://www.stcn.com',
        'search_url': 'https://www.stcn.com/search?keyword={keyword}',
        'selector': '.newslist li',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '经济观察网',
        'url': 'https://www.eeo.com.cn',
        'search_url': 'https://www.eeo.com.cn/search?keyword={keyword}',
        'selector': '.list_item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '金融时报',
        'url': 'https://www.financialnews.com.cn',
        'search_url': 'https://www.financialnews.com.cn/search?keyword={keyword}',
        'selector': '.news-list li',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.date'
    },
    {
        'name': '21世纪经济报道',
        'url': 'https://www.21jingji.com',
        'search_url': 'https://www.21jingji.com/search?keyword={keyword}',
        'selector': '.news-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '界面新闻',
        'url': 'https://www.jiemian.com',
        'search_url': 'https://www.jiemian.com/search?keyword={keyword}',
        'selector': '.news-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '华尔街见闻',
        'url': 'https://wallstreetcn.com',
        'search_url': 'https://wallstreetcn.com/search?keyword={keyword}',
        'selector': '.article-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '凤凰财经',
        'url': 'https://finance.ifeng.com',
        'search_url': 'https://search.ifeng.com/?q={keyword}&c=1',
        'selector': '.news-list-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '腾讯财经',
        'url': 'https://finance.qq.com',
        'search_url': 'https://www.sogou.com/web?query={keyword}',
        'selector': '.news-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '网易财经',
        'url': 'https://money.163.com',
        'search_url': 'https://money.163.com/search?keyword={keyword}',
        'selector': '.news-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    }
]

# 行业关键词
KEYWORDS = ['供应链', '金融', '物流', '航空', '融资', '贸易', '供应链金融', '银行', '证券', '基金', '保险', '投资', '经济', '产业', '数字化']

# 新闻数据文件路径
NEWS_FILE = 'news.json'
# 新闻数据过期时间（秒）
NEWS_EXPIRY = 30  # 30秒

def is_news_expired():
    """检查新闻数据是否过期"""
    if not os.path.exists(NEWS_FILE):
        return True
    
    # 检查文件修改时间
    file_mtime = os.path.getmtime(NEWS_FILE)
    current_time = time.time()
    
    return (current_time - file_mtime) > NEWS_EXPIRY

def extract_content(url):
    """从新闻详情页提取内容"""
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 尝试不同的内容选择器
        content_selectors = [
            '.article-content',
            '.content',
            '.article-body',
            '.main-content',
            '#content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text(strip=True)
                # 限制内容长度
                if len(content) > 200:
                    content = content[:200] + '...'
                return content
        
        # 如果没有找到内容，返回摘要
        return '点击查看详情'
    except Exception as e:
        print(f'提取内容失败: {e}')
        return '点击查看详情'

def crawl_news():
    """抓取新闻数据"""
    news_list = []
    
    for source in NEWS_SOURCES:
        try:
            # 如果有搜索URL，则使用搜索URL搜索关键字
            if 'search_url' in source:
                # 对每个关键字进行搜索
                for keyword in KEYWORDS[:3]:  # 只搜索前3个关键字，避免请求过多
                    search_url = source['search_url'].format(keyword=keyword)
                    print(f'正在搜索 {source["name"]} - 关键字: {keyword}...')
                    response = requests.get(search_url, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Connection': 'keep-alive'
                    })
                    response.encoding = 'utf-8'
                    
                    # 检查响应状态
                    if response.status_code != 200:
                        print(f'搜索 {source["name"]} 失败: 状态码 {response.status_code}')
                        continue
                    
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # 尝试使用多个选择器
                    selectors = [
                        source['selector'],
                        'li',
                        '.list-item',
                        '.article-item',
                        '.news',
                        '.item',
                        '.news-list li',
                        'ul li',
                        'div[class*="news"]',
                        'div[class*="article"]',
                        'a[href*="article"]'
                    ]
                    
                    items = []
                    for selector in selectors:
                        try:
                            found_items = soup.select(selector)
                            if found_items:
                                items = found_items
                                print(f'在 {source["name"]} 搜索结果中使用选择器 "{selector}" 找到 {len(items)} 条新闻')
                                break
                        except Exception as e:
                            print(f'使用选择器 "{selector}" 失败: {e}')
                    
                    if not items:
                        print(f'在 {source["name"]} 搜索结果中未找到新闻')
                        continue
                    
                    for item in items[:10]:  # 限制处理的新闻数量
                        # 提取标题和链接
                        try:
                            # 尝试不同的标题选择器
                            title_selectors = [
                                source['title_selector'],
                                'a',
                                'h3',
                                'h2',
                                '.title',
                                '.news-title',
                                '.article-title'
                            ]
                            
                            title_elem = None
                            for title_selector in title_selectors:
                                try:
                                    elem = item.select_one(title_selector)
                                    if elem and elem.text.strip() and len(elem.text.strip()) > 5:  # 确保标题长度足够
                                        title_elem = elem
                                        break
                                except Exception as e:
                                    print(f'使用标题选择器 "{title_selector}" 失败: {e}')
                            
                            if not title_elem:
                                continue
                            
                            title = title_elem.text.strip()
                            link = None
                            
                            # 尝试从标题元素或其父元素获取链接
                            if title_elem.get('href'):
                                link = title_elem.get('href')
                            else:
                                # 尝试从父元素获取链接
                                parent = title_elem.parent
                                while parent and not link:
                                    if parent.get('href'):
                                        link = parent.get('href')
                                        break
                                    parent = parent.parent
                            
                            if not link:
                                continue
                            
                            # 确保链接是完整的
                            if not link.startswith('http'):
                                if link.startswith('/'):
                                    link = source['url'] + link
                                else:
                                    link = source['url'] + '/' + link
                            
                            # 提取日期
                            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            if source['date_selector']:
                                try:
                                    date_elem = item.select_one(source['date_selector'])
                                    if date_elem:
                                        date_text = date_elem.text.strip()
                                        # 简单处理日期格式
                                        if date_text:
                                            date = date_text
                                except Exception as e:
                                    print(f'提取日期失败: {e}')
                            
                            # 检查是否包含关键词
                            if any(keyword in title for keyword in KEYWORDS):
                                # 提取内容
                                content = extract_content(link)
                                
                                news_item = {
                                    'title': title,
                                    'content': content,
                                    'link': link,
                                    'source': source['name'],
                                    'date': date,
                                    'image_prompt': f'{title} news professional'
                                }
                                news_list.append(news_item)
                                print(f'添加新闻: {title} - {source["name"]}')
                                
                                # 限制新闻数量
                                if len(news_list) >= 9:
                                    break
                        except Exception as e:
                            print(f'处理新闻项失败: {e}')
                            continue
                    
                    if len(news_list) >= 9:
                        break
            else:
                # 如果没有搜索URL，则直接抓取首页
                print(f'正在抓取 {source["name"]}...')
                response = requests.get(source['url'], timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive'
                })
                response.encoding = 'utf-8'
                
                # 检查响应状态
                if response.status_code != 200:
                    print(f'抓取 {source["name"]} 失败: 状态码 {response.status_code}')
                    continue
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # 尝试使用多个选择器
                selectors = [
                    source['selector'],
                    'li',
                    '.list-item',
                    '.article-item',
                    '.news',
                    '.item',
                    '.news-list li',
                    'ul li',
                    'div[class*="news"]',
                    'div[class*="article"]',
                    'a[href*="article"]'
                ]
                
                items = []
                for selector in selectors:
                    try:
                        found_items = soup.select(selector)
                        if found_items:
                            items = found_items
                            print(f'在 {source["name"]} 使用选择器 "{selector}" 找到 {len(items)} 条新闻')
                            break
                    except Exception as e:
                        print(f'使用选择器 "{selector}" 失败: {e}')
                
                if not items:
                    print(f'在 {source["name"]} 未找到新闻')
                    continue
                
                for item in items[:20]:  # 限制处理的新闻数量
                    # 提取标题和链接
                    try:
                        # 尝试不同的标题选择器
                        title_selectors = [
                            source['title_selector'],
                            'a',
                            'h3',
                            'h2',
                            '.title',
                            '.news-title',
                            '.article-title'
                        ]
                        
                        title_elem = None
                        for title_selector in title_selectors:
                            try:
                                elem = item.select_one(title_selector)
                                if elem and elem.text.strip() and len(elem.text.strip()) > 5:  # 确保标题长度足够
                                    title_elem = elem
                                    break
                            except Exception as e:
                                print(f'使用标题选择器 "{title_selector}" 失败: {e}')
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.text.strip()
                        link = None
                        
                        # 尝试从标题元素或其父元素获取链接
                        if title_elem.get('href'):
                            link = title_elem.get('href')
                        else:
                            # 尝试从父元素获取链接
                            parent = title_elem.parent
                            while parent and not link:
                                if parent.get('href'):
                                    link = parent.get('href')
                                    break
                                parent = parent.parent
                        
                        if not link:
                            continue
                        
                        # 确保链接是完整的
                        if not link.startswith('http'):
                            if link.startswith('/'):
                                link = source['url'] + link
                            else:
                                link = source['url'] + '/' + link
                        
                        # 提取日期
                        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        if source['date_selector']:
                            try:
                                date_elem = item.select_one(source['date_selector'])
                                if date_elem:
                                    date_text = date_elem.text.strip()
                                    # 简单处理日期格式
                                    if date_text:
                                        date = date_text
                            except Exception as e:
                                print(f'提取日期失败: {e}')
                        
                        # 检查是否包含关键词
                        if any(keyword in title for keyword in KEYWORDS):
                            # 提取内容
                            content = extract_content(link)
                            
                            news_item = {
                                'title': title,
                                'content': content,
                                'link': link,
                                'source': source['name'],
                                'date': date,
                                'image_prompt': f'{title} news professional'
                            }
                            news_list.append(news_item)
                            print(f'添加新闻: {title} - {source["name"]}')
                            
                            # 限制新闻数量
                            if len(news_list) >= 9:
                                break
                    except Exception as e:
                        print(f'处理新闻项失败: {e}')
                        continue
                        
        except Exception as e:
            print(f'抓取 {source["name"]} 失败: {e}')
        
        if len(news_list) >= 9:
            break
    
    # 确保至少有6条新闻
    if len(news_list) < 6:
        print(f'抓取的新闻数量不足6条，当前只有 {len(news_list)} 条，使用备用来源')
        # 如果抓取的新闻不够，使用备用来源
        backup_sources = [
            {
                'name': '新浪财经',
                'url': 'https://finance.sina.com.cn/stock/',
                'selector': '.news-item',
                'title_selector': 'a'
            },
            {
                'name': '东方财富网',
                'url': 'https://www.eastmoney.com',
                'selector': '.news-item',
                'title_selector': 'a'
            },
            {
                'name': '凤凰财经',
                'url': 'https://finance.ifeng.com',
                'selector': '.news-list-item',
                'title_selector': 'a'
            },
            {
                'name': '腾讯财经',
                'url': 'https://finance.qq.com',
                'selector': '.news-item',
                'title_selector': 'a'
            },
            {
                'name': '网易财经',
                'url': 'https://money.163.com',
                'selector': '.news-item',
                'title_selector': 'a'
            }
        ]
        
        for source in backup_sources:
            try:
                print(f'正在抓取备用来源 {source["name"]}...')
                response = requests.get(source['url'], timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive'
                })
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    print(f'抓取备用来源 {source["name"]} 失败: 状态码 {response.status_code}')
                    continue
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # 尝试使用多个选择器
                selectors = [
                    source['selector'],
                    'li',
                    '.list-item',
                    '.article-item',
                    '.news',
                    '.item',
                    '.news-list li',
                    'ul li',
                    'div[class*="news"]',
                    'div[class*="article"]',
                    'a[href*="article"]'
                ]
                
                items = []
                for selector in selectors:
                    try:
                        found_items = soup.select(selector)
                        if found_items:
                            items = found_items
                            print(f'在备用来源 {source["name"]} 使用选择器 "{selector}" 找到 {len(items)} 条新闻')
                            break
                    except Exception as e:
                        print(f'使用选择器 "{selector}" 失败: {e}')
                
                if not items:
                    print(f'在备用来源 {source["name"]} 未找到新闻')
                    continue
                
                for item in items[:20]:  # 限制处理的新闻数量
                    try:
                        # 尝试不同的标题选择器
                        title_selectors = [
                            source['title_selector'],
                            'a',
                            'h3',
                            'h2',
                            '.title',
                            '.news-title',
                            '.article-title'
                        ]
                        
                        title_elem = None
                        for title_selector in title_selectors:
                            try:
                                elem = item.select_one(title_selector)
                                if elem and elem.text.strip() and len(elem.text.strip()) > 5:  # 确保标题长度足够
                                    title_elem = elem
                                    break
                            except Exception as e:
                                print(f'使用标题选择器 "{title_selector}" 失败: {e}')
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.text.strip()
                        link = None
                        
                        # 尝试从标题元素或其父元素获取链接
                        if title_elem.get('href'):
                            link = title_elem.get('href')
                        else:
                            # 尝试从父元素获取链接
                            parent = title_elem.parent
                            while parent and not link:
                                if parent.get('href'):
                                    link = parent.get('href')
                                    break
                                parent = parent.parent
                        
                        if not link:
                            continue
                        
                        # 确保链接是完整的
                        if not link.startswith('http'):
                            if link.startswith('/'):
                                link = source['url'] + link
                            else:
                                link = source['url'] + '/' + link
                        
                        if any(keyword in title for keyword in KEYWORDS):
                            content = extract_content(link)
                            
                            news_item = {
                                'title': title,
                                'content': content,
                                'link': link,
                                'source': source['name'],
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'image_prompt': f'{title} news professional'
                            }
                            news_list.append(news_item)
                            print(f'添加备用新闻: {title} - {source["name"]}')
                            
                            if len(news_list) >= 9:
                                break
                    except Exception as e:
                        print(f'处理备用新闻项失败: {e}')
                        continue
            except Exception as e:
                print(f'抓取备用来源 {source["name"]} 失败: {e}')
            
            if len(news_list) >= 9:
                break
    
    # 确保至少有3条新闻
    if len(news_list) < 6:
        print(f'备用来源抓取失败，当前只有 {len(news_list)} 条新闻，使用最终备用新闻')
        # 使用用户提供的新浪网新闻链接作为初始内容
        final_backup = [
            {
                'title': '滨州"滨链通"供应链金融公共服务平台入驻企业超130家 累计业务规模破180亿元',
                'content': '滨州市滨链通供应链金融公共服务平台于2025年4月正式上线，具备供应链票据的签发、承兑、背书、融资、到期处理等全生命周期服务能力。截至目前，平台入驻的企业已超过130家，累计业务规模突破180亿元。',
                'link': 'https://k.sina.com.cn/article_1893761531_70e081fb020030zhi.html',
                'source': '新浪新闻',
                'date': '2026-03-27',
                'image_prompt': '供应链金融平台 滨州 滨链通'
            },
            {
                'title': '监管"十不准"与"77号文"层层加码，传统模式穷途末路，2026年，您的供应链金融业务该如何转型？',
                'content': '旧路径正在断裂。过去依赖主体信用、套利套汇的"搬运工"模式，在穿透式监管与真实贸易的要求下已难以为继。一边是合规红线的持续收紧，一边是利润空间的不断压缩，许多从业者正陷入"不做等死，做错找死"的双重困境。',
                'link': 'https://finance.sina.com.cn/wm/2026-03-27/doc-inhsnzav8948136.shtml',
                'source': '新浪财经',
                'date': '2026-03-27',
                'image_prompt': '供应链金融 监管 转型'
            },
            {
                'title': '平安银行：2025年供应链金融融资发生额19679亿元',
                'content': '平安银行在接受调研者提问时表示，2025年，公司供应链金融融资发生额19679亿元，同比增长23.1%。公司深入供应链场景，运用"金融+科技"能力不断创新业务模式，优化金融服务体验。',
                'link': 'https://cj.sina.com.cn/articles/view/2311077472/89c03e6002002ilh2',
                'source': '新浪财经',
                'date': '2026-03-27',
                'image_prompt': '平安银行 供应链金融 融资'
            },
            {
                'title': '这62页PPT，帮你看懂供应链金融！',
                'content': '本文通过62页PPT详细介绍了供应链金融的概念、模式、实践案例等内容，帮助读者全面了解供应链金融的运作机制和发展趋势。',
                'link': 'https://finance.sina.com.cn/wm/2026-03-26/doc-inhskfhh5647476.shtml',
                'source': '新浪财经',
                'date': '2026-03-26',
                'image_prompt': '供应链金融 PPT 教程'
            },
            {
                'title': '数实融合·链通全球——2026第十三届产业数字化与供应链金融创新论坛在深圳成功举行',
                'content': '2026年3月26日，由万联网主办的"第十三届产业数字化与供应链金融创新论坛"在深圳举办。近500位央国企/上市公司/行业龙头/供应链公司/物流商/科技服务商/金融机构高管精英齐聚一堂，共话生态供应链构建、国企供应链服务创新、物贸一体化转型及供应链合规风控等热点议题。',
                'link': 'https://finance.sina.com.cn/wm/2026-03-26/doc-inhsiqkn0144135.shtml',
                'source': '新浪财经',
                'date': '2026-03-26',
                'image_prompt': '产业数字化 供应链金融 论坛 深圳'
            },
            {
                'title': '数实融合趋势下，大宗供应链金融该如何赋能地方产业，实现细分领域的供应链升级？',
                'content': '在数字经济与实体经济深度融合的当下，大宗商品作为国民经济的"压舱石"，其供应链的稳定与高效直接关系到地方产业的韧性与竞争力。本文结合数实融合的发展趋势，立足地方产业发展实际，从现状剖析、赋能路径、保障措施三个方面，探讨大宗供应链金融如何助力地方细分领域供应链升级。',
                'link': 'https://finance.sina.com.cn/wm/2026-03-23/doc-inhrzcpn2201795.shtml',
                'source': '新浪财经',
                'date': '2026-03-23',
                'image_prompt': '数实融合 大宗供应链金融 地方产业'
            }
        ]
        
        news_list.extend(final_backup)
        # 限制最多9条
        news_list = news_list[:9]
        print(f'添加了 {len(final_backup)} 条最终备用新闻')
    
    # 保存新闻数据到文件
    news_data = {
        'timestamp': time.time(),
        'news': news_list
    }
    
    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    print(f'抓取完成，共获取 {len(news_list)} 条新闻')
    return news_list

def get_news():
    """获取最新新闻数据"""
    # 检查新闻数据是否过期
    if is_news_expired():
        return crawl_news()
    
    # 从文件中读取新闻数据
    try:
        with open(NEWS_FILE, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        return news_data['news']
    except Exception as e:
        print(f'读取新闻数据失败: {e}')
        return crawl_news()

if __name__ == '__main__':
    # 测试爬虫
    news = get_news()
    print(f'获取到 {len(news)} 条新闻')
    for i, item in enumerate(news):
        print(f'{i+1}. {item["title"]} - {item["source"]}')
        print(f'   链接: {item["link"]}')
        print(f'   内容: {item["content"]}')
        print()