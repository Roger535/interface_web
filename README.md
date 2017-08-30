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

## 说明

- 接口测试使用的是[requests](http://docs.python-requests.org/zh_CN/latest/user/quickstart.html) 框架