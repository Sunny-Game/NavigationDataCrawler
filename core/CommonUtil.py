from collections import OrderedDict

class CommonUtil:
    def sort_dict_bykey(self,old_dict, reverse=False):
        """对字典按key排序, 默认升序, 不修改原先字典"""
        # 先获得排序后的key列表
        keys = sorted(old_dict.keys(), reverse=reverse)
        # 创建一个新的空字典
        new_dict = OrderedDict()
        # 遍历 key 列表
        for key in keys:
            new_dict[key] = old_dict[key]
        return new_dict



