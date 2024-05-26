import os


class Info:
    def __init__(self, host='localhost', port=7555, device=False):
        '''
        连接前的准备，初始化app环境判断，默认连接夜神模拟器
        :param host:远程设备的ip地址，默认本机。
        :param port:远程设备的端口，默认夜视模拟器的端口。
        :param device:关键字参数，用于判断是不是USB直连设备，默认不是USB设备。
        '''
        if os.system('adb --version 1>nul 2>nul') == 0:
            if device:
                pass
            else:
                os.system('adb connect %s:%s' % (host, port))  # adb connect localhost:62001
        else:
            raise Exception('检查adb环境')

    def get_platform_name(self):    # 获取平台名
        cmd = 'adb shell getprop net.bt.name'
        data = os.popen(cmd)
        return list(data)[0].strip()

    def get_platform_version(self):     # 获取平台版本
        cmd = 'adb shell getprop ro.build.version.release'
        data = os.popen(cmd)
        return list(data)[0].strip()

    def get_device_name(self):      # 获取设备名
        cmd = 'adb devices'
        data = os.popen(cmd)
        return [i.strip() for i in list(data) if i.endswith('device\n')][0]

    def get_package_name(self, apkpath):    # 获取app名
        cmd = 'aapt dumpsys badging %s | findstr package' % apkpath
        # 因为popen执行返回的动态的数热流需要先缓存到内存中之后，通过read读取后进行转码操作
        data = os.popen(cmd)
        package_name = data.buffer.read().decode(encoding = 'utf-8').split("'")[1]
        return package_name

    def get_activity(self,apkpath):      # 获取activity名
        cmd = 'aapt dumpsys badging %s | findstr activity' % apkpath
        data = os.popen(cmd)
        # 因为popen执行返回的动态的数热流需要先缓存到内存中之后，通过read读取后进行转码操作
        activity = data.buffer.read().decode(encoding = 'utf-8').split("'")[1]
        return activity

    def install_app(self, apkpath):     # 安装app
        package_name = self.get_package_name(apkpath)
        flag = list(os.popen('adb shell pm list packages | findstr %s' % package_name))
        if flag:
            print('程序已经安装')
        else:
            cmd = 'adb install %s' % apkpath
            result = os.popen(cmd).read()  # 读取命令输出
            print('安装输出:', result)
            if "Success" in result:
                print('程序安装成功')
            else:
                print('程序安装失败')

    def uninstall_app(self,package_name):   # 卸载app
        flag = list(os.popen('adb shell pm list packages | findstr %s' % package_name))
        if flag:
            cmd = 'adb uninstall %s' % package_name
            os.system(cmd)
            print('程序已卸载')
        else:
            print('程序未安装')

    def clear_app(self,package):    # 重置app
        cmd = 'adb shell pm clear %s' %package
        os.system(cmd)
        print('程序已重置')


# if __name__ == '__main__':
    # apk = r'E:\Develop\App\xs.apk'
    # info = Info()
    # print(info.get_platform_name(), info.get_platform_version(), info.get_device_name(), info.get_package_name(apk))
    # info.install_app(apk)
    # info.uninstall_app(package)
    # info.clear_app(package)
    # package = info.get_package_name(apk)
    # package = info.get_activity(apk)
    # print(package)
