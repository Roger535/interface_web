# EAT (Easy Automation Test)

> 参照[**Google开源项目风格指南-Python**](http://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/python_style_rules/)
和[**JavaScript编码规范**](https://github.com/fex-team/styleguide/blob/master/javascript.md)
，我们的代码要求：
1. 注释风格规范
2. 命名风格规范
3. 代码格式规范

## 第一阶段 —— 接口自动化测试平台

## 引导

1. 确保已经安装了Python 2版本.
2. 确保已经安装Node.js
3. 启动项目

```
# 安装项目需要的python依赖模块
pip install -r requirements.txt

# 安装node下的依赖前端模块
npm install

# 全局安装Gulp 4 CLI工具
npm install gulpjs/gulp-cli -g

# 第一行命令可能会报错，不要紧接着执行下一条命令 
python ./manage.py migrate account
python ./manage.py migrate
python ./manage.py loaddata sites
python ./manage.py runserver
```

## 项目调试

1. 项目使用MySQL数据库，所以在启动项目前先要启动的本地的MySQL数据库服务，一般通过本地的MySQL客户端启动
2. Django启动服务命令需要在项目根目录下（manage.py同级目录）运行：```python manage.py runserver```
3. 如果修改了models.py里的表，需要先同步到本地数据库中，运行：```python manage.py migrate```，然后再运行上一步骤中的runserver命令
4. 如果需要运行项目tests目录下的py，运行：```python -m interface_platform.tests.xxxxx```

## 项目服务器配置
服务器配置参照该文档：http://cheng.logdown.com/posts/2015/01/27/deploy-django-nginx-gunicorn-on-mac-osx

1. 项目使用的Web服务器是[Gunicorn](http://gunicorn.org/)，代理服务器使用[Nginx](https://www.nginx.com/resources/wiki/)，对应的配置文件分别是根目录下的：gunicorn.conf.py和nginx.conf
2. Gunicorn的启动命令是在根目录下运行：```gunicorn -c gunicorn.conf.py interface_platform.wsgi```
3. Nginx的启动命令同样是在根目录下运行：```sudo nginx```
4. 如果更新了项目的JS或CSS这些静态文件，需要运行```python manage.py collectstatic``` 将所有静态文件更新到Nginx服务器静态文件目录，然后运行```sudo nginx -s reload```

## 其他说明

- 接口测试使用的是[requests](http://docs.python-requests.org/zh_CN/latest/user/quickstart.html) 框架



## 已实现功能（截止2017.02.22）

> 截止到今天，EAT平台原计划第一个版本的内容基本上全部开发完成，从**用例新建** --> **用例调试** --> **用例集新建** --> **用例集执行** --> **执行报告**整个完成的流程已基本实现，用户可以在平台上管理接口、全局变量、用例和用例执行集。

## 内容介绍

### 1. 项目介绍
![项目介绍图片](https://github.com/longmazhanfeng/interface_web/blob/master/wiki_res/%E9%A1%B9%E7%9B%AE%E4%BB%8B%E7%BB%8D.PNG)

* 项目主要功能模块：前端大量使用jQuery框架提供的AJAX技术对页面进行局部刷新，后端则基于Django基本视图中的TemplateView和部分静态方法来实现后端逻辑和数据处理；execution APP采用了新的框架和技术，前端使用AngularJS后端则使用了Django REST Framework框架，当然由于前期实现方式的影响和目录树的不同处理，前后端有少量使用AJAX和类的静态方法，具体在```execution\views.py```这个文件中可以了解到各自的代码。

* 教程可以借鉴 [**Getting Started with Django Rest Framework and AngularJS**](http://blog.kevinastone.com/getting-started-with-django-rest-framework-and-angularjs.html)。对项目后期的建议是继续采用这套框架或者更合适的前端或者后端框架，这样会大大简化开发流程、降低难度、提高效率和项目规范性。

* **项目的代码规范性，结构规范性一直都是十分重要的，之前的JS代码和部分后端逻辑py不符合规范建议后期有时间进行优化和调整。**

* 有关服务器的配置和使用请参照[项目首页](https://github.com/longmazhanfeng/interface_web)，如果有model修改，需要在项目根目录下先运行```python manage.py makemigrations```命令，后运行```python manage.py migrate```。

### 2. 后期计划

鉴于EAT平台开发至今还没有正式让用户体验在上面编写用例、调试用例和建立用例执行集，用户体验反馈和使用效果还未知，所以在组内正式推广后，用户会提出很多的意见和bug，针对用户体验上的容易实现的改进意见可以高优先级实现，大的难实现的意见加入后期开发需求池中，根据实际情况和难易程度，排好优先级再依次按计划实现。所以后期的计划建议是：
1. 组内推广，收集反馈，修复bug和提升用户体验
2. 完善执行报告细节部分，增加错误日志显示区域
3. 实现用例参数输入更灵活，类似testng数据格式（包括单接口多数据验证和单用例多数据验证）
4. 回收站
5. 对接开发的接口文档 --- 一键生成单接口
6. RF关键字和RF解析关键字逻辑，支持以前的用例集
 * RF接口测试支持
 * 上层逻辑支持

后续的所有计划请参照[EAT后续所有计划——让测试更容易](https://github.com/longmazhanfeng/interface_web)

## 开发技术

*  开发语言：Python 2.7.10
*  Web框架：Django 1.10.2 和 Django REST Framework
*  前端框架：Bootstrap、JQuery、AJAX、Angular
*  数据库：MySQL
*  服务器环境：Mac OS
*  开发工具：PyCharm

