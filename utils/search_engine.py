"""
搜索引擎模块 - 基于 Whoosh 的全文搜索
改编自 tg_searcher 项目，用于 TeleSubmit-v2
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import shutil

from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.writing import IndexWriter
from whoosh.query import Term, Or, DateRange, NumericRange, And
import whoosh.highlight as highlight
from jieba.analyse.analyzer import ChineseAnalyzer

logger = logging.getLogger(__name__)


class PostDocument:
    """搜索文档数据结构"""
    
    # 定义 Whoosh 索引结构
    schema = Schema(
        message_id=ID(stored=True, unique=True),
        post_id=NUMERIC(stored=True),  # 数据库ID，用于删除操作
        title=TEXT(stored=True, analyzer=ChineseAnalyzer()),
        description=TEXT(stored=True, analyzer=ChineseAnalyzer()),
        tags=TEXT(stored=True, analyzer=ChineseAnalyzer()),
        filename=TEXT(stored=True, analyzer=ChineseAnalyzer()),
        link=TEXT(stored=True),
        user_id=ID(stored=True),  # 使用 ID 类型支持大整数
        username=TEXT(stored=True),
        publish_time=DATETIME(stored=True, sortable=True),
        views=NUMERIC(stored=True),
        heat_score=NUMERIC(stored=True, sortable=True),
    )
    
    def __init__(self, message_id: int, title: str = "", description: str = "", 
                 tags: str = "", filename: str = "", link: str = "", user_id: int = 0, 
                 username: str = "", publish_time: datetime = None, 
                 views: int = 0, heat_score: float = 0, post_id: int = None):
        self.message_id = str(message_id)
        self.post_id = post_id  # 数据库ID
        self.title = title or ""
        self.description = description or ""
        self.tags = tags or ""
        self.filename = filename or ""
        self.link = link or ""
        self.user_id = user_id
        self.username = username or ""
        self.publish_time = publish_time or datetime.now()
        self.views = views
        self.heat_score = heat_score
    
    def as_dict(self):
        """转换为字典用于索引"""
        return {
            'message_id': self.message_id,
            'post_id': self.post_id if self.post_id is not None else 0,
            'title': self.title,
            'description': self.description,
            'tags': self.tags,
            'filename': self.filename,
            'link': self.link,
            'user_id': str(self.user_id),  # 转换为字符串以支持大整数
            'username': self.username,
            'publish_time': self.publish_time,
            'views': self.views,
            'heat_score': self.heat_score,
        }


class SearchHit:
    """搜索结果项"""
    
    def __init__(self, message_id: int, title: str, description: str, 
                 tags: str, filename: str, link: str, user_id: int, username: str,
                 publish_time: datetime, views: int, heat_score: float,
                 highlighted_title: str = "", highlighted_desc: str = "",
                 matched_fields: List[str] = None, post_id: int = None):
        self.message_id = message_id
        self.post_id = post_id  # 数据库ID，用于删除操作
        self.title = title
        self.description = description
        self.tags = tags
        self.filename = filename
        self.link = link
        self.user_id = user_id
        self.username = username
        self.publish_time = publish_time
        self.views = views
        self.heat_score = heat_score
        self.highlighted_title = highlighted_title or title
        self.highlighted_desc = highlighted_desc or description
        self.matched_fields = matched_fields or []  # 记录匹配的字段


class SearchResult:
    """搜索结果集"""
    
    def __init__(self, hits: List[SearchHit], total_results: int, 
                 is_last_page: bool, page_num: int):
        self.hits = hits
        self.total_results = total_results
        self.is_last_page = is_last_page
        self.page_num = page_num


class PostSearchEngine:
    """帖子搜索引擎 - 基于 Whoosh"""
    
    def __init__(self, index_dir: str = "search_index", from_scratch: bool = False):
        """
        初始化搜索引擎
        
        Args:
            index_dir: 索引目录路径
            from_scratch: 是否从头创建索引（清除现有数据）
        """
        self.index_dir = Path(index_dir)
        self.index_name = 'posts'
        
        # 创建索引目录
        if not self.index_dir.exists():
            self.index_dir.mkdir(parents=True)
        
        # 从头创建索引
        if from_scratch and self.index_dir.exists():
            logger.warning(f"清除现有索引: {self.index_dir}")
            shutil.rmtree(self.index_dir)
            self.index_dir.mkdir(parents=True)
        
        # 打开或创建索引
        if index.exists_in(str(self.index_dir), self.index_name):
            self.ix = index.open_dir(str(self.index_dir), self.index_name)
            logger.info(f"打开现有索引: {self.index_dir}")
        else:
            self.ix = index.create_in(str(self.index_dir), PostDocument.schema, self.index_name)
            logger.info(f"创建新索引: {self.index_dir}")
        
        # 创建查询解析器（支持多字段搜索）
        self.query_parser = MultifieldParser(
            ['title', 'description', 'tags', 'filename'],
            schema=PostDocument.schema
        )
        
        # 创建高亮器
        self.highlighter = highlight.Highlighter(
            fragmenter=highlight.ContextFragmenter(maxchars=200, surround=50),
            formatter=highlight.HtmlFormatter()
        )
    
    def add_post(self, post: PostDocument, writer: Optional[IndexWriter] = None):
        """
        添加帖子到索引
        
        Args:
            post: 帖子文档
            writer: 可选的写入器（用于批量操作）
        """
        if writer is not None:
            writer.add_document(**post.as_dict())
        else:
            with self.ix.writer() as writer:
                writer.add_document(**post.as_dict())
        logger.debug(f"添加帖子到索引: {post.message_id}")
    
    def update_post(self, post: PostDocument):
        """
        更新帖子索引
        
        Args:
            post: 帖子文档
        """
        with self.ix.writer() as writer:
            writer.update_document(**post.as_dict())
        logger.debug(f"更新帖子索引: {post.message_id}")
    
    def delete_post(self, message_id: int):
        """
        从索引中删除帖子
        
        Args:
            message_id: 消息 ID
        """
        with self.ix.writer() as writer:
            writer.delete_by_term('message_id', str(message_id))
        logger.debug(f"从索引删除帖子: {message_id}")
    
    def search(self, query_str: str, page_num: int = 1, page_len: int = 10,
               time_filter: Optional[DateRange] = None,
               user_filter: Optional[int] = None,
               tag_filter: Optional[str] = None,
               sort_by: str = "publish_time") -> SearchResult:
        """
        搜索帖子
        
        Args:
            query_str: 搜索关键词
            page_num: 页码（从1开始）
            page_len: 每页结果数量
            time_filter: 时间过滤器
            user_filter: 用户ID过滤
            tag_filter: 标签过滤
            sort_by: 排序字段（publish_time 或 heat_score）
        
        Returns:
            SearchResult: 搜索结果
        """
        try:
            # 解析查询
            if query_str.strip():
                q = self.query_parser.parse(query_str)
            else:
                # 空查询时返回所有结果
                from whoosh.query import Every
                q = Every()
            
            # 构建过滤条件
            filters = []
            
            if time_filter:
                filters.append(time_filter)
            
            if user_filter is not None:
                filters.append(Term('user_id', str(user_filter)))  # 转换为字符串
            
            if tag_filter:
                # 标签精确匹配
                filters.append(Term('tags', tag_filter))
            
            # 合并过滤条件
            q_filter = None
            if filters:
                if len(filters) == 1:
                    q_filter = filters[0]
                else:
                    q_filter = And(filters)
            
            # 执行搜索
            with self.ix.searcher() as searcher:
                result_page = searcher.search_page(
                    q, 
                    page_num, 
                    page_len,
                    filter=q_filter,
                    sortedby=sort_by,
                    reverse=True
                )
                
                # 构建结果
                hits = []
                for hit in result_page:
                    # 高亮显示
                    highlighted_title = self.highlighter.highlight_hit(hit, 'title') or hit.get('title', '')
                    highlighted_desc = self.highlighter.highlight_hit(hit, 'description') or hit.get('description', '')
                    
                    # 检测匹配字段
                    matched_fields = []
                    if query_str.strip():
                        # 简单检查：看看查询词是否在各个字段中
                        query_lower = query_str.lower()
                        if hit.get('title', '').lower().find(query_lower) != -1:
                            matched_fields.append('标题')
                        if hit.get('description', '').lower().find(query_lower) != -1:
                            matched_fields.append('简介')
                        if hit.get('tags', '').lower().find(query_lower) != -1:
                            matched_fields.append('标签')
                        if hit.get('filename', '').lower().find(query_lower) != -1:
                            matched_fields.append('文件名')
                    
                    search_hit = SearchHit(
                        message_id=int(hit.get('message_id', 0)),
                        post_id=int(hit.get('post_id', 0)) if hit.get('post_id') else None,
                        title=hit.get('title', ''),
                        description=hit.get('description', ''),
                        tags=hit.get('tags', ''),
                        filename=hit.get('filename', ''),
                        link=hit.get('link', ''),
                        user_id=hit.get('user_id', 0),
                        username=hit.get('username', ''),
                        publish_time=hit.get('publish_time', datetime.now()),
                        views=hit.get('views', 0),
                        heat_score=hit.get('heat_score', 0),
                        highlighted_title=highlighted_title,
                        highlighted_desc=highlighted_desc,
                        matched_fields=matched_fields
                    )
                    hits.append(search_hit)
                
                return SearchResult(
                    hits=hits,
                    total_results=result_page.total,
                    is_last_page=result_page.is_last_page(),
                    page_num=page_num
                )
        
        except Exception as e:
            logger.error(f"搜索失败: {e}", exc_info=True)
            # 返回空结果
            return SearchResult(hits=[], total_results=0, is_last_page=True, page_num=page_num)
    
    def get_stats(self) -> dict:
        """
        获取索引统计信息
        
        Returns:
            dict: 统计信息
        """
        with self.ix.searcher() as searcher:
            return {
                'total_docs': searcher.doc_count_all(),
                'indexed_fields': list(self.ix.schema.names()),
            }
    
    def clear(self):
        """清空索引"""
        if self.index_dir.exists():
            shutil.rmtree(self.index_dir)
            self.index_dir.mkdir(parents=True)
            self.ix = index.create_in(str(self.index_dir), PostDocument.schema, self.index_name)
            logger.info("索引已清空")
    
    def is_empty(self) -> bool:
        """检查索引是否为空"""
        return self.ix.is_empty()


# 全局搜索引擎实例（单例模式）
_search_engine: Optional[PostSearchEngine] = None


def get_search_engine(index_dir: str = "search_index") -> PostSearchEngine:
    """
    获取全局搜索引擎实例
    
    Args:
        index_dir: 索引目录
    
    Returns:
        PostSearchEngine: 搜索引擎实例
    """
    global _search_engine
    if _search_engine is None:
        _search_engine = PostSearchEngine(index_dir)
    return _search_engine


def init_search_engine(index_dir: str = "search_index", from_scratch: bool = False):
    """
    初始化搜索引擎
    
    Args:
        index_dir: 索引目录
        from_scratch: 是否从头创建
    """
    global _search_engine
    _search_engine = PostSearchEngine(index_dir, from_scratch)
    logger.info("搜索引擎初始化完成")

