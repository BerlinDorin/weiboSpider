import traceback

from .util import handle_html
from .parser import Parser
from .info_parser import InfoParser


class IndexParser(Parser):
    def __init__(self, cookie, user_uri):
        self.cookie = cookie
        self.user_uri = user_uri
        self.url = "https://weibo.cn/%s" % (user_uri)
        self.selector = handle_html(self.cookie, self.url)

    def _get_user_id(self):
        """获取用户id，使用者输入的user_id不一定是正确的，可能是个性域名等，需要获取真正的user_id"""
        user_id = self.user_uri
        url_list = self.selector.xpath("//div[@class='u']//a")
        for url in url_list:
            if (url.xpath("string(.)")) == u"资料":
                if url.xpath("@href") and url.xpath("@href")[0].endswith("/info"):
                    link = url.xpath("@href")[0]
                    user_id = link[1:-5]
                    break
        return user_id

    def get_user(self):
        """获取用户信息、微博数、关注数、粉丝数"""
        try:
            self.user = {}
            self.user["id"] = self._get_user_id()
            user = InfoParser(self.cookie, self.user["id"]).extract_user_info()  # 获取用户信息
            for k, v in user.items():
                self.user[k] = v
            user_info = self.selector.xpath("//div[@class='tip2']/*/text()")
            weibo_num = int(user_info[0][3:-1])
            following = int(user_info[1][3:-1])
            followers = int(user_info[2][3:-1])
            self.user["weibo_num"] = weibo_num
            self.user["following"] = following
            self.user["followers"] = followers
            return self.user
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_page_num(self):
        """获取微博总页数"""
        try:
            if self.selector.xpath("//input[@name='mp']") == []:
                page_num = 1
            else:
                page_num = (int)(
                    self.selector.xpath("//input[@name='mp']")[0].attrib["value"]
                )
            return page_num
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()