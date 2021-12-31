import os
import shutil


def remove_path(path):
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


class PathSyncer:
    """
    路径同步器，路径可以是文件和目录
    """

    def __init__(self, sour_path, dest_path, sync_paths=None, ignore_paths=None):
        """
        :param sour_path: 需要同步的源路径
        :param dest_path: 需要同步的目标路径
        :param sync_paths: 可以指定只同步指定路径，如果不输入则同步所有路径，参数为路径的数组
        :param ignore_paths: 可以指定同步时忽略的路径，参数为路径的数组
        """
        if sour_path is None or sour_path == '':
            raise ValueError('sour_path is missing')
        if dest_path is None or dest_path == '':
            raise ValueError('dest_path is missing')

        self.sour_path = os.path.normpath(sour_path)
        self.dest_path = os.path.normpath(dest_path)

        if sync_paths is not None:
            for i in range(0, len(sync_paths)):
                sync_paths[i] = os.path.normpath(sync_paths[i])
        self.sync_paths = sync_paths

        if ignore_paths is not None:
            for i in range(0, len(ignore_paths)):
                ignore_paths[i] = os.path.normpath(ignore_paths[i])
        self.ignore_paths = ignore_paths

    def sync(self):
        """
        开始同步
        :return: None
        """
        if os.path.isdir(self.sour_path):
            self._sync_dir(self.sour_path, self.dest_path)
        else:
            self._sync_file(self.sour_path, self.dest_path)

    def _sync_file(self, sour, dest):
        if os.path.isfile(sour) and self._is_sync_path(os.path.relpath(sour, self.sour_path), False):
            print(sour + ' -> ' + dest)
            if os.path.isdir(dest):
                shutil.rmtree(dest)
            shutil.copy(sour, dest)

    def _sync_dir(self, sour, dest):
        if os.path.isfile(dest):
            os.remove(dest)

        # 创建目标目录
        need_del = True
        if not os.path.isdir(dest):
            need_del = False  # 新建的目录没必要再检查删除的文件
            print('mkdir ' + dest)
            os.makedirs(dest)

        # 拷贝新增或修改的文件
        for p in os.listdir(sour):
            sour_path = os.path.join(sour, p)
            dest_path = os.path.join(dest, p)

            if os.path.isfile(sour_path) and self._is_sync_path(os.path.relpath(sour_path, self.sour_path), False):
                print(sour_path + ' -> ' + dest_path)
                shutil.copy(sour_path, dest_path)
            elif os.path.isdir(sour_path) and self._is_sync_path(os.path.relpath(sour_path, self.sour_path), True):
                self._sync_dir(sour_path, dest_path)

    def _is_sync_path(self, rel_path, is_dir):
        can_sync = True
        if self.sync_paths is not None:
            can_sync = False
            for p in self.sync_paths:
                if (is_dir and p.startswith(rel_path)) or rel_path.startswith(p):
                    can_sync = True
                    break

        if not can_sync:
            return False

        if self.ignore_paths is not None:
            for p in self.ignore_paths:
                if (is_dir and p.startswith(rel_path)) and rel_path.startswith(p):
                    return False
        return True
