## 订场脚本使用

> 当前脚本适用于预订东校球场

#### 环境配置

Python环境参考

![image-20250408123817053](README.assets/image-20250408123817053.png)

需安装第三方库：

```cmd
pip install pyyaml requests
```

#### 账号配置

1. 打开浏览器登录账号
2. `F12` 或 右键选择`检查` 开启开发人员工具，如下图。点击`Network`

<img src="README.assets/image-20250408115120409.png" alt="image-20250408115120409"  />

3. 刷新页面，随意点击Type为xhr的条目

![image-20250408115420964](README.assets/image-20250408115420964.png)

如下图，找到`Headers`→`Authorization`，将`Bearer`以下的内容全部**复制**

![image-20250408115652260](README.assets/image-20250408115652260.png)

4. 打开`accounts.yaml`文件

   - 将**复制内容**粘贴到`token`中代表一个账号，每个账号配置`court_1`、`time_1`表示预订场地和时间，`court_2`、`time_2`同理，如果只预订一个场则在`court_2`处填写 0。

   - 配置多个账号在下面自行扩展格式一致的`token`、`court_1`、`time_1`、`court_2`、`time_2`即可。
   - 修改第二个红框中的`date`订场日期，`target_time`一般都是22点。

![image-20250408120500198](README.assets/image-20250408120500198.png)

​	`User_Agent`：如果本机初次使用最好改一下，在下图中可以找到

![image-20250408120847712](README.assets/image-20250408120847712.png)

#### 运行脚本

打开命令行，运行`start.py`：

```
python start.py
```

得到以下图片的输出表示预订成功

![image-20250408122136166](README.assets/image-20250408122136166.png)



**其他输出**

1. 该账号当天已经预订

![image-20250408122439562](README.assets/image-20250408122439562.png)

2. 预订时间未到时，或填写的日期不正确

![image-20250408122537925](README.assets/image-20250408122537925.png)

3. 短时间内刷新发送请求太多次了

![image-20250408122708113](README.assets/image-20250408122708113.png)

4. 身份信息过期

   - 重新刷新页面复制`Authorization`的信息到`accounts.yaml`文件的`token`中（过一段时间Authorization就会刷新

   - 检查`accounts.yaml`文件的`User_Agent`是否和浏览器一致

   ![image-20250408122930056](README.assets/image-20250408122930056.png)