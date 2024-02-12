# Image Repository API

这是一个 RESTful 风格的图库 API，使用 Python Flask 框架编写。此项目作为 iceDeer 工作室的后端示例项目。

## 项目结构

```
orm/ # 对象关系映射
    user.py # 用户、令牌黑名单模型
    image.py # 图片模型
    album.py # 图集、图集图片关联模型
resources/ # 资源
    user.py # 用户、登录、登出、刷新令牌资源
    image.py # 图片资源
    album.py # 图集资源
    util.py # 测试工具资源
tests/ # 测试
    test_user.py
    test_image.py
    test_album.py
app.py # 应用入口
config.py # 配置
models.py # 定义数据模型
jwt_auth.py # 自定义 JWT 认证
extensions.py # 创建 SQLAlchemy 和 Flask-RESTX 对象
requirements.txt # 依赖
.env.example # 环境变量示例
Dockfile # Docker 镜像构建文件
```

## 运行

### 使用 Docker

```bash
docker build -t image-repository-api .
docker run -p 8080:8080 --env-file .env image-repository-api
```

### 使用 Python

```bash
pip install -r requirements.txt
flask run # 测试环境
waitress-serve --call 'app:create_app' # 生产环境
```

## 文档

文档使用 Flask-RESTX 由代码中的定义自动生成。运行应用后，访问 `/docs` 即可查看文档。

## 测试
    
运行测试：

```bash
python tests/test_user.py
python tests/test_image.py
python tests/test_album.py
```

另请参阅 [Tests.md](tests.md)。