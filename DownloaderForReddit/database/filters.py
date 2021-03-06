import traceback
from abc import ABC
from sqlalchemy.sql import func
from sqlalchemy import or_
from sqlalchemy import desc as descending
from sqlalchemy import Integer, String, DateTime, Enum

from .models import (RedditObjectList, RedditObject, User, Subreddit, DownloadSession, Post, Content, Comment,
                     ListAssociation)
from .model_enums import NsfwFilter


class Filter(ABC):
    """
    An abstract class that filters database model queries based on a list of supplied tuples that correspond to model
    attributes.
    """

    op_map = {
        'eq': lambda attr, value: attr == value,
        'not': lambda attr, value: attr != value,
        'lt': lambda attr, value: or_(attr == None, attr < value),
        'lte': lambda attr, value: or_(attr == None, attr <= value),
        'gt': lambda attr, value: attr > value,
        'gte': lambda attr, value: attr >= value,
        'in': lambda attr, value: attr.in_(value),
        'like': lambda attr, value: attr.like(f'%{value}%'),
        'contains': lambda attr, value: attr.contains(value)
    }

    model = None
    default_order = 'id'
    filter_include = []
    filter_exclude = []
    order_by_include = []
    order_by_exclude = []
    choices = {}

    session = None

    @classmethod
    def get_filter_fields(cls):
        if len(cls.filter_include) == 0:
            cls.filter_include = cls.model.__table__.columns.keys()
        elif 'all' in cls.filter_include:
            cls.filter_include.remove('all')
            cls.filter_include.extend(cls.model.__table__.columns.keys())
        for x in cls.filter_exclude:
            cls.remove_item(cls.filter_include, x)
        cls.filter_include.sort()
        return cls.filter_include

    @classmethod
    def get_order_fields(cls):
        if len(cls.order_by_include) == 0 or 'all' in cls.order_by_include:
            cls.order_by_include.extend(cls.model.__table__.columns.keys())
            for x in cls.order_by_exclude:
                cls.remove_item(cls.order_by_include, x)
            cls.remove_item(cls.order_by_include, 'all')
        cls.order_by_include.sort()
        return cls.order_by_include

    @staticmethod
    def remove_item(item_list, item):
        try:
            item_list.remove(item)
        except ValueError:
            pass

    def __init__(self):
        self.custom_filter_map = {}

    def filter(self, session, *filters, query=None, order_by=None, desc=False):
        self.session = session
        if query is None:
            query = session.query(self.model)
        for tup in filters:
            key, operator, value = tup
            attr = getattr(self.model, key, None)
            if not attr:
                query = self.custom_filter(query, key, operator, value)
                continue
            if operator == 'in':
                if not isinstance(value, list):
                    value = value.split(',')
            try:
                f = self.op_map[operator](attr, value)
                query = query.filter(f)
            except Exception as e:
                traceback.print_exc()
        query = self.order_query(query, order_by, desc)
        return query

    def order_query(self, query, order, desc):
        if order is None:
            order = self.default_order
        order_by = getattr(self.model, order, None)
        if order_by is None or isinstance(order_by, property):
            try:
                query, order_by = self.custom_filter_map[order].order_method(query)
            except KeyError:
                print('key error')
                order_by = self.default_order
        if desc:
            order_by = descending(order_by)
        return query.order_by(order_by)

    def custom_filter(self, query, attr, operator, value):
        try:
            return self.custom_filter_map[attr].filter_method(query, operator, value)
        except KeyError:
            return query

    def get_type(self, attr):
        if self.choices.get(attr, None) is not None:
            return Enum
        try:
            return type(self.model.__table__.c[attr].type)
        except KeyError:
            try:
                return self.custom_filter_map[attr].field_type
            except KeyError:
                return None

    def get_choices(self, attr):
        choices = self.choices.get(attr, None)
        if choices is not None:
            return choices
        try:
            choices = []
            field = self.model.__table__.c[attr]
            if type(field.type) == Enum:
                enum = field.type.enum_class
                for value in enum:
                    choices.append((value.display_name.title(), value))
                return choices
        except KeyError:
            return self.custom_filter_map[attr].choices
        except AttributeError:
            return None
        return None

    def get_custom_filter_item(self, attr):
        return self.custom_filter_map[attr]


class RedditObjectListFilter(Filter):
    model = RedditObjectList
    default_order = 'name'
    filter_include = ['all', 'reddit_object_count', 'total_score']
    filter_exclude = ['post_score_limit_operator', 'comment_score_limit_operator']
    order_by_include = ['name', 'date_created', 'list_type', 'reddit_object_count', 'total_score', 'date_limit']
    choices = {'list_type': ['USER', 'SUBREDDIT']}

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'reddit_object_count': CustomItem(self.filter_reddit_object_count, self.order_by_reddit_object_count,
                                              Integer),
            'post_count': CustomItem(self.filter_post_count, self.order_by_post_count, Integer),
            'total_score': CustomItem(self.filter_total_score, self.order_by_total_score, Integer),
        }

    def get_reddit_object_count_sub(self):
        return self.session.query(ListAssociation.reddit_object_list_id,
                                  func.count(ListAssociation.reddit_object_id).label('ro_count')) \
            .group_by(ListAssociation.reddit_object_list_id).subquery()

    def get_post_count_sub(self):
        return self.session.query(ListAssociation.reddit_object_list_id, Post.significant_reddit_object_id,
                                  func.count(Post.id).label('post_count')) \
            .join(Post, Post.significant_reddit_object_id == ListAssociation.reddit_object_id) \
            .group_by(ListAssociation.reddit_object_list_id).subquery()

    def get_total_score_sub(self):
        return self.session.query(ListAssociation.reddit_object_list_id, Post.significant_reddit_object_id,
                                  func.sum(Post.score).label('total_score')) \
            .join(Post, Post.significant_reddit_object_id == ListAssociation.reddit_object_id) \
            .group_by(ListAssociation.reddit_object_list_id).subquery()

    def join_query(self, query, sub):
        return query.outerjoin(sub, RedditObjectList.id == sub.c.reddit_object_list_id)

    def filter_reddit_object_count(self, query, operator, value):
        sub = self.get_reddit_object_count_sub()
        f = self.op_map[operator](sub.c.ro_count, value)
        query = self.join_query(query, sub).filter(f)
        return query

    def filter_post_count(self, query, operator, value):
        sub = self.get_post_count_sub()
        f = self.op_map[operator](sub.c.post_count, value)
        query = self.join_query(query, sub).filter(f)
        return query

    def filter_total_score(self, query, operator, value):
        sub = self.get_total_score_sub()
        f = self.op_map[operator](sub.c.total_score, value)
        query = self.join_query(query, sub).filter(f)
        return query

    def order_by_reddit_object_count(self, query):
        sub = self.get_reddit_object_count_sub()
        query = self.join_query(query, sub)
        return query, sub.c.ro_count

    def order_by_post_count(self, query):
        sub = self.get_post_count_sub()
        query = self.join_query(query, sub)
        return query, sub.c.post_count

    def order_by_total_score(self, query):
        sub = self.get_total_score_sub()
        query = self.join_query(query, sub)
        return query, sub.c.total_score


class RedditObjectFilter(Filter):
    model = RedditObject
    default_order = 'name'
    filter_include = ['all', 'post_score', 'post_count', 'comment_score', 'comment_count', 'download_count',
                      'last_post_date', 'list_count']
    filter_exclude = ['post_score_limit_operator', 'comment_score_limit_operator', 'lists']
    order_by_include = ['id', 'name', 'last_download', 'date_added', 'absolute_date_limit', 'date_created',
                        'post_score', 'post_count', 'content_count', 'comment_count', 'download_count',
                        'last_post_date', 'list_count']
    choices = {'object_type': ['USER', 'SUBREDDIT']}

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'post_score': CustomItem(self.filter_post_score, self.order_by_score, Integer),
            'post_count': CustomItem(self.filter_post_count, self.order_by_post_count, Integer),
            'comment_score': CustomItem(self.filter_comment_score, self.order_by_comment_score, Integer),
            'comment_count': CustomItem(self.filter_comment_count, self.order_by_comment_count, Integer),
            'content_count': CustomItem(self.filter_content_count, self.order_by_content_count, Integer),
            'download_count': CustomItem(self.filter_download_count, self.order_by_download_count, Integer),
            'last_post_date': CustomItem(self.filter_last_post_date, self.order_by_last_post_date, DateTime),
            'list_count': CustomItem(self.filter_list_count, self.order_by_list_count, Integer),
        }

    def get_score_sum_sub(self):
        return self.session.query(Post.significant_reddit_object_id, func.sum(Post.score).label('total_score')) \
            .group_by(Post.significant_reddit_object_id).subquery()

    def get_post_count_sub(self):
        return self.session.query(Post.significant_reddit_object_id, func.count(Post.id).label('post_count')) \
            .group_by(Post.significant_reddit_object_id).subquery()

    def get_comment_score_sub(self):
        return self.session.query(Post.significant_reddit_object_id, func.sum(Comment.score).label('total_score')) \
            .join(Post).group_by(Post.significant_reddit_object_id).subquery()

    def get_comment_count_sub(self):
        return self.session.query(Post.significant_reddit_object_id, func.count(Comment.id).label('comment_count')) \
            .join(Post).group_by(Post.significant_reddit_object_id).subquery()

    def get_content_count_sub(self):
        return self.session.query(Post.significant_reddit_object_id, func.count(Content.id).label('content_count')) \
            .join(Post).group_by(Post.significant_reddit_object_id).subquery()

    def get_download_count_sub(self):
        return self.session.query(Post.significant_reddit_object_id,
                                  func.count(Post.download_session_id.distinct()).label('dl_count')) \
            .group_by(Post.significant_reddit_object_id).subquery()

    def get_last_post_date_sub(self):
        return self.session.query(Post.significant_reddit_object_id,
                                  func.max(Post.date_posted).label('last_post_date')) \
            .group_by(Post.significant_reddit_object_id).subquery()

    def get_list_count_sub(self):
        return self.session.query(ListAssociation.reddit_object_id,
                                  func.count(ListAssociation.reddit_object_list_id.distinct()).label('list_count'))\
               .group_by(ListAssociation.reddit_object_id).subquery()

    def join_queries(self, query, sub):
        return query.outerjoin(sub, RedditObject.id == sub.c.significant_reddit_object_id)

    def filter_post_score(self, query, operator, value):
        sub = self.get_score_sum_sub()
        f = self.op_map[operator](sub.c.total_score, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_post_count(self, query, operator, value):
        sub = self.get_post_count_sub()
        f = self.op_map[operator](sub.c.post_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_comment_score(self, query, operator, value):
        sub = self.get_comment_score_sub()
        f = self.op_map[operator](sub.c.total_score, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_comment_count(self, query, operator, value):
        sub = self.get_comment_count_sub()
        f = self.op_map[operator](sub.c.comment_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_content_count(self, query, operator, value):
        sub = self.get_content_count_sub()
        f = self.op_map[operator](sub.c.content_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_download_count(self, query, operator, value):
        sub = self.get_download_count_sub()
        f = self.op_map[operator](sub.c.dl_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_last_post_date(self, query, operator, value):
        sub = self.get_last_post_date_sub()
        f = self.op_map[operator](sub.c.last_post_date, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_list_count(self, query, operator, value):
        sub = self.get_list_count_sub()
        f = self.op_map[operator](sub.c.list_count, value)
        query = query.outerjoin(sub, RedditObject.id == sub.c.reddit_object_id).filter(f)
        return query

    def order_by_score(self, query):
        sub = self.get_score_sum_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.total_score

    def order_by_post_count(self, query):
        sub = self.get_post_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.post_count

    def order_by_comment_score(self, query):
        sub = self.get_comment_score_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.comment_score

    def order_by_comment_count(self, query):
        sub = self.get_comment_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.comment_count

    def order_by_content_count(self, query):
        sub = self.get_content_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.content_count

    def order_by_download_count(self, query):
        sub = self.get_download_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.dl_count

    def order_by_last_post_date(self, query):
        sub = self.get_last_post_date_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.last_post_date

    def order_by_list_count(self, query):
        sub = self.get_list_count_sub()
        query = query.outerjoin(sub, RedditObject.id == sub.c.reddit_object_id)
        return query, sub.c.list_count


class DownloadSessionFilter(Filter):
    model = DownloadSession
    default_order = 'id'
    included = ['all', 'reddit_object_count', 'post_count', 'comment_count', 'content_count', 'total_activity_count']
    excluded = ['extraction_thread_count', 'download_thread_count']
    filter_include = included
    filter_exclude = excluded
    order_by_include = included
    order_by_exclude = excluded

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'reddit_object_count': CustomItem(self.filter_reddit_object_count, self.order_by_reddit_object_count,
                                              Integer),
            'post_count': CustomItem(self.filter_post_count, self.order_by_post_count, Integer),
            'comment_count': CustomItem(self.filter_comment_count, self.order_by_comment_count, Integer),
            'content_count': CustomItem(self.filter_content_count, self.order_by_content_count, Integer),
            'total_activity_count': CustomItem(self.filter_total_activity_count, self.order_by_total_activity_count,
                                               Integer)
        }

    def get_reddit_object_count_sub(self):
        return self.session.query(Post.download_session_id,
                                  func.count(Post.significant_reddit_object_id.distinct()).label('ro_count')) \
            .group_by(Post.download_session_id).subquery()

    def get_post_count_sub(self):
        return self.session.query(Post.download_session_id, func.count(Post.id).label('post_count')) \
            .group_by(Post.download_session_id).subquery()

    def get_comment_count_sub(self):
        return self.session.query(Comment.download_session_id, func.count(Comment.id).label('comment_count')) \
            .group_by(Comment.download_session_id).subquery()

    def get_content_count_sub(self):
        return self.session.query(Content.download_session_id, func.count(Content.id).label('content_count')) \
            .group_by(Content.download_session_id).subquery()

    def get_total_activity_sub(self):
        return self.get_post_count_sub(), self.get_comment_count_sub(), self.get_content_count_sub()

    def join_queries(self, query, sub):
        return query.outerjoin(sub, DownloadSession.id == sub.c.download_session_id)

    def filter_reddit_object_count(self, query, operator, value):
        sub = self.get_reddit_object_count_sub()
        f = self.op_map[operator](sub.c.ro_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_post_count(self, query, operator, value):
        sub = self.get_post_count_sub()
        f = self.op_map[operator](sub.c.post_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_comment_count(self, query, operator, value):
        sub = self.get_comment_count_sub()
        f = self.op_map[operator](sub.c.comment_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_content_count(self, query, operator, value):
        sub = self.get_content_count_sub()
        f = self.op_map[operator](sub.c.content_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_total_activity_count(self, query, operator, value):
        post_sub, comment_sub, content_sub = self.get_total_activity_sub()
        f = self.op_map[operator](
            (func.coalesce(post_sub.c.post_count, 0) +
             func.coalesce(content_sub.c.content_count, 0) +
             func.coalesce(comment_sub.c.comment_count, 0)),
            value
        )
        query = query \
            .outerjoin(post_sub, post_sub.c.download_session_id == DownloadSession.id) \
            .outerjoin(content_sub, content_sub.c.download_session_id == DownloadSession.id) \
            .outerjoin(comment_sub, comment_sub.c.download_session_id == DownloadSession.id) \
            .filter(f)
        return query

    def order_by_reddit_object_count(self, query):
        sub = self.get_reddit_object_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.ro_count

    def order_by_post_count(self, query):
        sub = self.get_post_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.post_count

    def order_by_comment_count(self, query):
        sub = self.get_comment_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.comment_count

    def order_by_content_count(self, query):
        sub = self.get_content_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.content_count

    def order_by_total_activity_count(self, query):
        post_sub, comment_sub, content_sub = self.get_total_activity_sub()
        query = query \
            .outerjoin(post_sub, post_sub.c.download_session_id == DownloadSession.id) \
            .outerjoin(content_sub, content_sub.c.download_session_id == DownloadSession.id) \
            .outerjoin(comment_sub, comment_sub.c.download_session_id == DownloadSession.id)
        return query, \
               (func.coalesce(post_sub.c.post_count, 0) +
                func.coalesce(content_sub.c.content_count, 0) +
                func.coalesce(comment_sub.c.comment_count, 0)).label('total_activity')


class PostFilter(Filter):
    model = Post
    default_order = 'title'
    include = ['all', 'author_name', 'subreddit_name', 'comment_count', 'content_count']
    exclude = ['author_id', 'subreddit_id', 'significant_reddit_object_id', 'download_session_id']
    filter_include = include
    filter_exclude = exclude
    order_by_include = include
    order_by_exclude = exclude

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'comment_count': CustomItem(self.filter_comment_count, self.order_by_comment_count, Integer),
            'content_count': CustomItem(self.filter_content_count, self.order_by_content_count, Integer),
            'author_name': CustomItem(self.filter_author_name, self.order_by_author_name, String),
            'subreddit_name': CustomItem(self.filter_subreddit_name, self.order_by_subreddit_name, String),
        }

    def get_comment_count_sub(self):
        return self.session.query(Comment.post_id, func.count(Comment.id).label('comment_count')) \
            .group_by(Comment.post_id).subquery()

    def get_content_count_sub(self):
        return self.session.query(Content.post_id, func.count(Content.id).label('content_count')) \
            .group_by(Content.post_id).subquery()

    def join_queries(self, query, sub):
        return query.outerjoin(sub, Post.id == sub.c.post_id)

    def filter_comment_count(self, query, operator, value):
        sub = self.get_comment_count_sub()
        f = self.op_map[operator](sub.c.comment_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_content_count(self, query, operator, value):
        sub = self.get_content_count_sub()
        f = self.op_map[operator](sub.c.content_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_author_name(self, query, operator, value):
        f = self.op_map[operator](User.name, value)
        return query.join(User, User.id == Post.author_id).filter(f)

    def filter_subreddit_name(self, query, operator, value):
        f = self.op_map[operator](Subreddit.name, value)
        return query.join(Subreddit, Subreddit.id == Post.subreddit_id).filter(f)

    def order_by_author_name(self, query):
        query = query.join(User, User.id == Post.author_id)
        return query, User.name

    def order_by_subreddit_name(self, query):
        query = query.join(Subreddit, Subreddit.id == Post.subreddit_id)
        return query, Subreddit.name

    def order_by_comment_count(self, query):
        sub = self.get_comment_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.comment_count

    def order_by_content_count(self, query):
        sub = self.get_content_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.content_count


class CommentFilter(Filter):
    model = Comment
    default_order = 'id'
    include = ['all', 'post_score', 'post_date', 'nsfw', 'author_name', 'subreddit_name']
    exclude = ['author_id', 'subreddit_id', 'post_id', 'download_session_id']
    filter_include = include
    filter_exclude = exclude
    order_by_include = include
    order_by_exclude = exclude

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'post_title': CustomItem(self.filter_post_title, self.order_by_post_title, String),
            'post_score': CustomItem(self.filter_post_score, self.order_by_post_score, Integer),
            'post_date': CustomItem(self.filter_post_date, self.order_by_post_date, DateTime),
            'nsfw': CustomItem(self.filter_nsfw, field_type=Enum,
                               choices=[(x.display_name.title(), x) for x in NsfwFilter]),
            'author_name': CustomItem(self.filter_author_name, self.order_by_author_name, String),
            'subreddit_name': CustomItem(self.filter_subreddit_name, self.order_by_subreddit_name, String),
            'content_count': CustomItem(self.filter_content_count, self.order_by_content_count, Integer)
        }

    def get_content_count_sub(self):
        return self.session.query(Content.comment_id, func.count(Content.id).label('content_count')) \
            .group_by(Content.comment_id).subquery()

    def filter_post_title(self, query, operator, value):
        f = self.op_map[operator](Post.title, value)
        query = query.join(Post).filter(f)
        return query

    def filter_post_score(self, query, operator, value):
        f = self.op_map[operator](Post.score, value)
        query = query.join(Post).filter(f)
        return query

    def filter_post_date(self, query, operator, value):
        f = self.op_map[operator](Post.date_posted, value)
        query = query.join(Post).filter(f)
        return query

    def filter_nsfw(self, query, operator, value):
        f = self.op_map[operator](Post.nsfw, value)
        query = query.join(Post).filter(f)
        return query

    def filter_author_name(self, query, operator, value):
        f = self.op_map[operator](User.name, value)
        query = query.join(User, User.id == Comment.author_id).filter(f)
        return query

    def filter_subreddit_name(self, query, operator, value):
        f = self.op_map[operator](Subreddit.name, value)
        query = query.join(Subreddit, Subreddit.id == Comment.subreddit_id).filter(f)
        return query

    def filter_content_count(self, query, operator, value):
        sub = self.get_content_count_sub()
        f = self.op_map[operator](sub.c.content_count, value)
        query = query.outerjoin(sub, sub.c.comment_id == Comment.id).filter(f)
        return query

    def order_by_post_title(self, query):
        return query.join(Post), Post.title

    def order_by_post_score(self, query):
        return query.join(Post), Post.score

    def order_by_post_date(self, query):
        return query.join(Post), Post.date_posted

    def order_by_author_name(self, query):
        return query.join(User, User.id == Comment.author_id), User.name

    def order_by_subreddit_name(self, query):
        return query.join(Subreddit, Subreddit.id == Comment.subreddit_id), Subreddit.name

    def order_by_content_count(self, query):
        sub = self.get_content_count_sub()
        query = query.outerjoin(sub, sub.c.comment_id == Comment.id)
        return query, sub.c.content_count


class ContentFilter(Filter):
    model = Content
    default_order = 'title'
    include = ['all', 'post_score', 'post_date', 'nsfw', 'domain', 'author_name', 'subreddit_name']
    exclude = ['user_id', 'subreddit_id', 'post_id', 'comment_id', 'download_session_id']
    filter_include = include
    filter_exclude = exclude
    order_by_include = include
    order_by_exclude = exclude

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'post_score': CustomItem(self.filter_post_score, self.order_by_post_score, Integer),
            'post_date': CustomItem(self.filter_date_posted, self.order_by_date_posted, DateTime),
            'nsfw': CustomItem(self.filter_nsfw, field_type=Enum,
                               choices=[(x.display_name.title(), x) for x in NsfwFilter]),
            'domain': CustomItem(self.filter_domain, self.order_by_domain, String),
            'author_name': CustomItem(self.filter_author_name, self.order_by_author_name, String),
            'subreddit_name': CustomItem(self.filter_subreddit_name, self.order_by_subreddit_name, String),
        }

    def filter_post_score(self, query, operator, value):
        f = self.op_map[operator](Post.score, value)
        query = query.join(Post).filter(f)
        return query

    def filter_date_posted(self, query, operator, value):
        f = self.op_map[operator](Post.date_posted, value)
        query = query.join(Post).filter(f)
        return query

    def filter_nsfw(self, query, operator, value):
        f = self.op_map[operator](Post.nsfw, value)
        query = query.join(Post).filter(f)
        return query

    def filter_domain(self, query, operator, value):
        f = self.op_map[operator](Post.domain, value)
        query = query.join(Post).filter(f)
        return query

    def filter_author_name(self, query, operator, value):
        f = self.op_map[operator](User.name, value)
        query = query.join(User, User.id == Content.user_id).filter(f)
        return query

    def filter_subreddit_name(self, query, operator, value):
        f = self.op_map[operator](Subreddit.name, value)
        query = query.join(Subreddit, Subreddit.id == Content.subreddit_id).filter(f)
        return query

    def order_by_post_score(self, query):
        return query.join(Post, Post.id == Content.post_id), Post.score

    def order_by_date_posted(self, query):
        return query.join(Post, Post.id == Content.post_id), Post.date_posted

    def order_by_domain(self, query):
        return query.join(Post, Post.id == Content.post_id), Post.domain

    def order_by_author_name(self, query):
        return query.join(User, User.id == Content.user_id), User.name

    def order_by_subreddit_name(self, query):
        return query.join(Subreddit, Subreddit.id == Content.subreddit_id), Subreddit.name


class CustomItem:

    def __init__(self, filter_method=None, order_method=None, field_type=String, choices=None):
        self.filter_method = filter_method
        self.order_method = order_method
        self.field_type = field_type
        self.choices = choices
